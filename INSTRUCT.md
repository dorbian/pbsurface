# Product instructions

## Purpose

Build a resilient, offline-capable BlackBerry PlayBook client that operates as
a remote display, touch/input terminal, camera/microphone endpoint, and
Stream-Deck-style control surface for modern computers.

## Product shape

- Keep rendering, decoding, discovery and input capture native on the PlayBook.
- Keep capture, encoding, automation integrations and arbitrary host behavior on
  modern endpoints.
- Support multiple discoverable endpoints and explicit user selection.
- Make control-deck actions endpoint-owned and allowlisted.
- Treat Bitfocus Companion as an optional high-leverage integration, not a
  requirement for basic actions.
- Operate without BlackBerry services once the archived toolchain is installed.

## Safety boundaries

- Never commit firmware, SDK archives, private keys, device backups or tokens.
- Never accept arbitrary shell strings over the network.
- Never expose the control service directly to the public internet.
- Keep device flashing and unsigned-code enablement separate from normal builds.
- Do not claim PlayBook hardware support until behavior is accepted on a device.

## Completion authority

Emulator and host tests are necessary but do not prove device behavior. Media,
touch, audio, suspend/resume and BAR installation milestones require explicit
hardware acceptance.

