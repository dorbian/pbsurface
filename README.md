# PlayBook Surface

PlayBook Surface gives the BlackBerry PlayBook a useful second life as a native
network display, remote input surface, and configurable control deck.

The modern endpoint does the expensive work. It captures and H.264-encodes a
display, executes locally approved actions, and can bridge Bitfocus Companion.
The PlayBook discovers endpoints, decodes the media stream, renders buttons,
and sends touch events back.

## Current state

This repository is an initial, testable foundation. It currently contains:

- a dependency-free Python endpoint service with UDP discovery;
- authenticated, allowlisted action execution without shell parsing;
- a versioned protocol and security contract;
- a placeholder tree for the PlayBook Native SDK client;
- deterministic full-source ZIP creation and verification;
- a ZipRunner project manifest for full ZIP and Git patch workflows.

It does not yet stream video or contain a buildable PlayBook BAR. Those begin
after a real PlayBook and the archived Tablet OS 2.1 Native SDK are available
for hardware acceptance.

## Run the host prototype

Python 3.11 or newer is recommended.

1. Copy `config/endpoint.example.json` to `local/endpoint.json`.
2. Replace the example token with a long random value.
3. Run:

   ```powershell
   python run_host.py --config local/endpoint.json
   ```

The service listens for `PBSURFACE_DISCOVER/1` UDP broadcasts on port 47881 and
exposes a small authenticated prototype API on port 47880. Keep it on a trusted
private network.

## Validate and package

```powershell
python -m unittest discover -s tests -v
python tools/package_source.py
python tools/verify_package.py dist/playbook-surface-0.1.0-source.zip
```

The generated source ZIP is intended for ZipRunner's normal safe overlay path.
Incremental work can instead be delivered as ZipRunner `.patch` or `.diff`
artifacts bound to the exact Git base revision. See `docs/ZIPRUNNER.md`.

## Repository boundaries

Firmware, SDK installers, signing material, device backups, tokens and private
endpoint configuration are deliberately excluded. Their names and checksums may
be recorded locally, but proprietary or secret material must not be committed.

