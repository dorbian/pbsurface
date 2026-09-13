# PlayBook Surface protocol v1

## Discovery

The PlayBook broadcasts the exact UTF-8 datagram:

```text
PBSURFACE_DISCOVER/1
```

Endpoints listening on UDP 47881 reply directly to the sender with no more than
4096 bytes of UTF-8 JSON:

```json
{
  "schema": "playbook-surface.discovery/v1",
  "protocol": 1,
  "id": "stable-random-endpoint-id",
  "name": "Gaming PC",
  "control_port": 47880,
  "capabilities": ["actions", "deck", "display", "input"]
}
```

Discovery establishes no trust and carries no token or executable instruction.

## Prototype control API

The initial host exposes:

- `GET /health` — unauthenticated liveness only;
- `GET /v1/endpoint` — authenticated endpoint metadata;
- `GET /v1/deck` — authenticated button page;
- `POST /v1/actions/{action_id}` — authenticated allowlisted action invocation.

Authenticated requests carry `X-PlayBook-Token`. This HTTP API is a development
surface for a private LAN, not the final device control transport.

## Deck model

A deck has an identifier, title, column count and bounded button collection.
Every button has a numeric position, opaque action identifier and presentation
fields. The endpoint rejects action identifiers not present in its local action
registry.

## Planned control transport

After PlayBook hardware acceptance, the native client will use a persistent,
length-prefixed connection for:

- pairing challenge and proof;
- endpoint and page state;
- key press/release/hold events;
- pointer, touch, gesture and keyboard events;
- stream negotiation and status feedback.

The protocol will retain the endpoint/action model above. Arbitrary remote shell
commands are permanently out of scope.

## Planned media transport

The preferred first hardware test is H.264 video plus AAC audio in MPEG-TS over
RTP. Target profiles begin at 1024x600, 30 fps and 2–4 Mbit/s. The exact profile
is not normative until tested against PlayBook `mm-renderer` hardware decoding.

