# ZipRunner management

PlayBook Surface supports ZipRunner's two existing source-management lanes.

## Full source ZIP

Run `python tools/package_source.py`. The deterministic artifact is named:

```text
playbook-surface-<version>-source.zip
```

`project.zr` matches that name, strips the single package root and protects Git,
local configuration, legacy toolchains, firmware, device backups, generated
packages and logs during overlay. ZipRunner remains responsible for validation,
backup, build and explicit apply/release gates.

## Incremental patch

Once the repository has an initial Git commit, add `playbook-surface` as a
ZipRunner patch target through ZipRunner's **Add repository** workflow. Patch
artifacts use ZipRunner's current UTF-8 unified-diff metadata contract and exact
40-character base commit. Patch apply/commit/push remain separate gates.

Do not manually edit ZipRunner's active configuration merely to onboard this
repository. Use its project/import and patch-target UI so paths and Git state are
validated before persistence.

## Artifact boundaries

Neither source ZIPs nor patches may contain:

- BlackBerry SDK or firmware archives;
- `.bar` or `.signed` binaries;
- signing keys, pairing tokens or endpoint configuration;
- device backups;
- build output or runtime logs.

