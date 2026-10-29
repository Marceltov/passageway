---
status: accepted
date: 2026-10-29
decision-makers: Marcel Bruckner (the direction), Claude (the write-up under the goal of building the roadmap to the end)
---

# The Confluence connector targets Data Center first

## Context and Problem Statement

Confluence comes in two kinds that differ in authentication and API paths: Data Center (and Server) authenticates a personal access token with `Authorization: Bearer` under `/rest/api`, Cloud authenticates an e-mail address with an API token under `/wiki/rest/api` (and a newer v2 API). The roadmap left the choice open. Which does the connector support first?

## Considered Options

* Data Center first: a personal access token, spaces by key, pages listed with ids and versions, changes by CQL.
* Cloud first.
* Both at once, behind a `KIND` setting.

## Decision Outcome

Chosen option: "Data Center first", because that is what the predecessor's proposal described (a personal access token kept as a secret, spaces by key, a listing of ids and versions, changes since a time) and what the author's own use needs. Cloud is a later addition behind a setting; nothing in the item mapping depends on the kind.

### Consequences

* Good, because one authentication scheme and one API shape are tested through an in-test server, and the mapping (sections at `h1` to `h3`, labels, ancestors as the path, every page weighing 1.0) is the same for Cloud later.
* Bad, because Atlassian Cloud users have to wait; the README says so.
* The connector is written from the public REST documentation and tested against a fake of it, not a live site; the first run against a real Data Center is the owner's.
