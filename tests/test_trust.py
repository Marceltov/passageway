"""Every HTTPS client verifies against the operating system's trust store, not certifi's bundle (#66)."""

import ssl
import urllib.error

import pytest
import truststore
from passageway_connector_confluence import connector as confluence
from passageway_connector_trilium import connector as trilium
from passageway_connector_wikipedia.mediawiki import Wiki
from passageway_embedder_openai import embedder as openai

from passageway import models


def _context(client):
    return client._transport._pool._ssl_context


def test_every_http_client_uses_the_system_trust_store():
    clients = [
        confluence.Api(confluence.parse_settings({"URL": "https://wiki.example", "SPACES": "OPS", "TOKEN": "t"}))._http,
        trilium.Etapi(trilium.parse_settings({"URL": "https://notes.example", "TOKEN": "t"}))._http,
        Wiki("https://en.wikipedia.org/w/api.php", "test")._http,
        openai.Embedder(openai.parse_settings({"MODEL": "m", "API_KEY": "k"}))._http,
    ]
    for client in clients:
        assert isinstance(_context(client), truststore.SSLContext)


def test_verify_tls_false_still_turns_checking_off():
    s = confluence.parse_settings({"URL": "https://wiki.example", "SPACES": "OPS", "TOKEN": "t", "VERIFY_TLS": "false"})
    assert _context(confluence.Api(s)._http).verify_mode == ssl.CERT_NONE


def test_the_model_download_uses_the_system_trust_store(tmp_path, monkeypatch):
    seen = {}

    def urlopen(request, *, timeout, context):
        seen["context"] = context
        raise urllib.error.URLError("offline")

    monkeypatch.setattr(models.urllib.request, "urlopen", urlopen)
    with pytest.raises(models.ModelError):
        models.download(models.PRESETS[models.DEFAULT_PRESET], tmp_path / "m")
    assert isinstance(seen["context"], truststore.SSLContext)
