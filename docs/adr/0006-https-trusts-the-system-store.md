---
status: accepted
date: 2026-10-30
decision-makers: Marcel Bruckner (the direction), Claude (the write-up)
---

# HTTPS clients trust the operating system's certificate store

## Context and Problem Statement

httpx and urllib check certificates against certifi's bundle, which knows the public CAs and nothing else. A Confluence or Trilium behind a company or internal CA, trusted in the macOS Keychain, the Windows store or `/etc/ssl`, failed with `CERTIFICATE_VERIFY_FAILED` while Safari and curl reached it. The ways out were `VERIFY_TLS=false`, which turns checking off, or a hand-exported bundle in `SSL_CERT_FILE`, which goes stale (#66). Where should trust come from, and where should the code that sets it live?

## Considered Options

* Every client passes `truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)`, one line in each package, each package depending on `truststore` itself.
* One helper in the SDK that every client calls.
* `truststore.inject_into_ssl()` once at start-up.

## Decision Outcome

Chosen option: "one line in each package". The SDK promises no dependencies, the markdown connector makes no HTTP request, and neither the embedder nor the core depends on the SDK, so a helper there would pull the SDK and `truststore` into places that have no use for them, all to share one line. `inject_into_ssl()` patches `ssl` for the whole process and every library in it, which is more than a client should decide for its neighbours.

### Consequences

* Good, because a CA the operating system trusts works everywhere without a setting, and certificate checking stays on.
* Good, because `tests/test_trust.py` lists every client, and CLAUDE.md makes a new client join it.
* Bad, because the line is repeated in five places; a sixth client has to remember it, which the test and the rule are there for.
