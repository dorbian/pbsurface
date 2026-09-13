# Agent entry point

Read in this order before changing the project:

1. `INSTRUCT.md`
2. `DESIGN.adoc`
3. `PROJECT_PLAN.adoc`
4. `CODING.md`
5. `TESTING.md`
6. `project.zr`

## Working contract

- Preserve the offline build path and the host/PlayBook boundary.
- Keep network formats versioned and backward compatible within a major version.
- Add focused tests for protocol, package, security and action changes.
- Keep shell interpretation disabled for endpoint actions.
- Do not add proprietary firmware, SDKs, certificates, keys or device backups.
- Update design and protocol documents when their contracts change.
- Do not mark PlayBook behavior complete without real-device evidence.
- ZIP apply, patch commit, push, tag and release remain separate ZipRunner gates.

