import json
import os
import sys
import threading
import time

import numpy as np
import pytest

from passageway.embed import HashEmbedder
from passageway.embed_command import CommandEmbedder, EmbedderError

CMD = [sys.executable, "-m", "passageway.testing.fake_embedder"]


def make(tmp_path, *, fail="", name="fake-hash", dim=64, secrets=None, extra_env=None, **kw):
    log = tmp_path / "embed.log"
    env = {"FAKE_EMBED_LOG": str(log), "FAKE_EMBED_NAME": name, "FAKE_EMBED_DIM": str(dim), **(extra_env or {})}
    if fail:
        env["FAKE_EMBED_FAIL"] = fail
    embedder = CommandEmbedder("test", CMD, env=env, secrets=secrets or {}, **kw)
    return embedder, log


def records(log):
    return [json.loads(line) for line in log.read_text().splitlines()]


def requests(log, op="embed"):
    return [r["request"] for r in records(log) if "request" in r and r["request"]["op"] == op]


@pytest.fixture
def embedder(tmp_path):
    e, log = make(tmp_path)
    e.log = log
    yield e
    e.close()


def test_the_name_and_dimension_come_from_info(embedder):
    assert (embedder.name, embedder.dim) == ("fake-hash", 64)


def test_vectors_are_unit_length_float32_in_the_order_of_the_texts(embedder):
    out = embedder.embed_passages(["alpha beta", "gamma", "alpha beta"])
    assert out.shape == (3, 64) and out.dtype == np.float32
    assert np.allclose(np.linalg.norm(out, axis=1), 1.0, atol=1e-5)
    assert np.allclose(out[0], out[2]) and not np.allclose(out[0], out[1])
    expected = HashEmbedder(64).embed_passages(["alpha beta", "gamma"])
    assert np.allclose(out[:2], expected, atol=1e-5)


def test_queries_and_passages_are_told_apart_by_kind(embedder):
    embedder.embed_queries(["q"])
    embedder.embed_passages(["p"])
    assert [(r["kind"], r["texts"]) for r in requests(embedder.log)] == [("query", ["q"]), ("passage", ["p"])]


def test_no_texts_need_no_request(embedder):
    out = embedder.embed_queries([])
    assert out.shape == (0, 64) and requests(embedder.log) == []


def test_texts_are_sent_in_batches_and_come_back_in_order(tmp_path):
    e, log = make(tmp_path, batch_size=32)
    try:
        texts = [f"word{i} common" for i in range(70)]
        out = e.embed_passages(texts)
        assert [len(r["texts"]) for r in requests(log)] == [32, 32, 6]
        assert np.allclose(out, HashEmbedder(64).embed_passages(texts), atol=1e-5)
    finally:
        e.close()


def test_one_process_serves_every_call(embedder):
    embedder.embed_queries(["a"])
    embedder.embed_queries(["b"])
    assert len({r["pid"] for r in records(embedder.log)}) == 1


def test_the_process_gets_an_empty_environment_plus_its_own_settings(tmp_path, monkeypatch):
    monkeypatch.setenv("PASSAGEWAY_LOGIN_PASSWORD", "the-servers-password")
    monkeypatch.setenv("SOME_OTHER_SECRET", "x")
    e, log = make(tmp_path, secrets={"API_KEY": "k"}, extra_env={"MODEL": "bge"})
    try:
        seen = set(records(log)[0]["env"])
    finally:
        e.close()
    assert {"PATH", "HOME", "PASSAGEWAY_PROTOCOL", "MODEL", "API_KEY", "FAKE_EMBED_LOG"} <= seen
    assert "PASSAGEWAY_LOGIN_PASSWORD" not in seen and "SOME_OTHER_SECRET" not in seen


def test_an_error_reply_fails_that_call_with_the_message_and_not_the_process(tmp_path):
    e, log = make(tmp_path, fail="error")
    try:
        with pytest.raises(EmbedderError, match="out of memory"):
            e.embed_queries(["x"])
        with pytest.raises(EmbedderError, match="out of memory"):  # still alive: it answered again
            e.embed_queries(["y"])
        assert len({r["pid"] for r in records(log)}) == 1
    finally:
        e.close()


def test_a_process_that_died_between_calls_is_restarted_once_and_the_call_succeeds(tmp_path):
    e, log = make(tmp_path, fail="die-after:1")
    try:
        first = e.embed_queries(["one"])
        second = e.embed_queries(["two"])  # the process exits on this request: restart, ask again
        assert first.shape == second.shape == (1, 64)
        assert len({r["pid"] for r in records(log)}) == 2
    finally:
        e.close()


def test_a_process_that_keeps_dying_fails_the_call_with_its_masked_error_output(tmp_path):
    e, log = make(tmp_path, fail="always-die", secrets={"FAKE_SECRET": "hunter2"})
    try:
        with pytest.raises(EmbedderError) as error:
            e.embed_queries(["x"])
    finally:
        e.close()
    assert "fake died" in str(error.value) and "hunter2" not in str(error.value) and "***" in str(error.value)
    assert len({r["pid"] for r in records(log)}) == 2  # restarted once, not forever


def test_a_process_that_does_not_start_fails_the_constructor_with_its_error_output(tmp_path):
    with pytest.raises(EmbedderError, match="fake start failure"):
        make(tmp_path, fail="start")


def test_a_failing_info_is_an_error(tmp_path):
    with pytest.raises(EmbedderError, match="no model loaded"):
        make(tmp_path, fail="info-error")


def test_another_protocol_version_is_refused(tmp_path):
    with pytest.raises(EmbedderError, match="protocol"):
        make(tmp_path, fail="protocol2")


def test_a_request_that_takes_too_long_fails_and_kills_the_process(tmp_path):
    e, log = make(tmp_path, fail="hang", timeout=0.5)
    try:
        started = time.monotonic()
        with pytest.raises(EmbedderError, match="timed out"):
            e.embed_queries(["x"])
        assert time.monotonic() - started < 5
        pid = records(log)[0]["pid"]
        time.sleep(0.2)
        with pytest.raises(ProcessLookupError):
            os.kill(pid, 0)  # gone
    finally:
        e.close()


@pytest.mark.parametrize("fail,message", [("garbage", "not json|JSON|line 1"), ("not-an-object", "object"), ("count", "vectors"),
                                          ("dim", "dimension|dim"), ("nan", "finite|number"), ("zero", "zero|length")])
def test_a_reply_that_is_not_a_proper_answer_is_an_error_naming_the_problem(tmp_path, fail, message):
    e, _ = make(tmp_path, fail=fail)
    try:
        with pytest.raises(EmbedderError, match=message):
            e.embed_passages(["one", "two"])
    finally:
        e.close()


def test_a_line_longer_than_the_limit_is_an_error(tmp_path):
    e, _ = make(tmp_path, max_line_bytes=2000)
    try:
        with pytest.raises(EmbedderError, match="longer than"):
            e.embed_passages([f"text {i}" for i in range(32)])  # 32 vectors of 64 floats are more than 2000 bytes
    finally:
        e.close()


def test_a_restart_that_brings_up_another_model_is_refused(tmp_path):
    name_file = tmp_path / "name"
    e, log = make(tmp_path, fail="die-after:1", extra_env={"FAKE_EMBED_NAME_FILE": str(name_file)})
    try:
        e.embed_queries(["one"])
        name_file.write_text("a-different-model")  # the restarted process will call itself something else
        with pytest.raises(EmbedderError, match="a-different-model|identity|name"):
            e.embed_queries(["two"])
    finally:
        e.close()


def test_calls_from_several_threads_do_not_mix_their_answers(tmp_path):
    e, _ = make(tmp_path)
    errors = []

    def work(i):
        text = f"thread {i} says something unique{i}"
        try:
            got = e.embed_queries([text])[0]
            if not np.allclose(got, HashEmbedder(64).embed_queries([text])[0], atol=1e-5):
                errors.append(i)
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)

    try:
        threads = [threading.Thread(target=work, args=(i,)) for i in range(12) for _ in range(3)]
        [t.start() for t in threads]
        [t.join() for t in threads]
    finally:
        e.close()
    assert errors == []


def test_close_stops_the_process_and_a_closed_embedder_says_so(tmp_path):
    e, log = make(tmp_path)
    pid = records(log)[0]["pid"]
    e.close()
    time.sleep(0.2)
    with pytest.raises(ProcessLookupError):
        os.kill(pid, 0)
    with pytest.raises(EmbedderError, match="closed"):
        e.embed_queries(["x"])
    e.close()  # twice is fine


def test_a_process_that_never_reads_cannot_hang_a_request_bigger_than_the_pipe(tmp_path):
    e, log = make(tmp_path, fail="no-read", timeout=1.0, batch_size=32)
    try:
        started = time.monotonic()
        with pytest.raises(EmbedderError, match="timed out"):
            e.embed_passages(["x" * 8000 for _ in range(32)])  # 256 KB: more than a pipe holds
        assert time.monotonic() - started < 8
    finally:
        e.close()
