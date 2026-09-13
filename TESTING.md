# Testing

## Standard validation

```powershell
python -m unittest discover -s tests -v
python -m compileall host/src tools run_host.py
```

## Package validation

```powershell
python tools/package_source.py
python tools/verify_package.py dist/playbook-surface-0.1.0-source.zip
```

The verifier must reject traversal paths, duplicate members, unexpected root
names, missing manifests, hash mismatches and files excluded by the source
package policy.

## Hardware validation

Hardware-dependent milestones need a recorded device model, OS version and:

- unsigned BAR installation result;
- launch, suspend/resume and reboot behavior;
- touch and bezel gesture evidence;
- H.264/AAC stream profile, latency and stability;
- audio routing and synchronization;
- memory use and battery behavior.

