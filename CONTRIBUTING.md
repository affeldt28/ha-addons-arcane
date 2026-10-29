# Contributing

Issues and pull requests are welcome. For bugs, include the add-on version, CPU architecture, Home Assistant version, reproduction steps and logs with credentials removed.

## Repository layout

- `arcane_edge_agent/`: Monitor's local image build, startup script and fixed Docker API policy.
- `arcane_edge_agent_full/`: Full Access image inheriting the pinned official Arcane image with only Home Assistant labels.
- `tests/`: configuration checks, Docker integration tests and their helpers.
- `.github/workflows/validate.yml`: CI validation.

Each add-on has its own README, setup documentation, changelog, translations, icon and logo. Add-on manifests use YAML.

Monitor uses Docker's init (`init: true`) and supervises its two processes in its startup script. It does not use S6. Monitor reads Supervisor options and retains pairing settings in the public add-on configuration folder. Full Access uses Supervisor legacy option-to-environment forwarding and mounts its public folder at `/app/data`, without a custom startup script. Neither agent needs host networking, exposed host ports or Supervisor API permissions.

## Local validation

```sh
python3 -m pip install -r tests/requirements.txt
sh -n arcane_edge_agent/rootfs/usr/local/bin/run-monitor
shellcheck arcane_edge_agent/rootfs/usr/local/bin/run-monitor
python3 tests/check_policy.py
python3 -m unittest discover -s tests -p 'test_*.py'
python3 tests/integration.py
```

The integration test requires a running Docker daemon. It builds both packages and tests the actual proxy with a fake Docker socket, then verifies unprivileged startup, shutdown and the permission guard. The real host Docker socket is never mounted into test containers. Temporary test containers and volumes are removed afterward; the built test image remains cached.

CI authenticates to GHCR with a read-only job token and retries explicit registry rate-limit failures. Other build failures still fail immediately. Keep these checks intact when changing startup or access policy.

For changes to Docker access, verify both allowed monitoring requests and blocked write/file-download requests. Never broaden the allowlist merely to remove an Arcane UI error. Test installation, pairing, persistence and backup/restore on Home Assistant OS before declaring a release stable.

## Publishing an update

1. Update the relevant add-on's configuration version and changelog.
2. For Monitor, also update the Dockerfile's default `BUILD_VERSION` when changing the package version. Its upstream Arcane and proxy tags are pinned separately.
3. Full Access is also built locally. Its `Dockerfile` pins the upstream image independently of the package version. For a packaging-only fix, increment the suffix (for example `2.16.1-1` → `2.16.1-2`) in `config.yaml`, leaving the upstream `BUILD_FROM` default unchanged. Supervisor supplies the Home Assistant labels from `config.yaml`; do not duplicate them in the Dockerfile. For an Arcane upgrade, update the pinned tag and the package version together.
4. Run the relevant checks, commit and push to the branch users have installed.
5. Home Assistant discovers the new version when its store refreshes. Users update through Home Assistant; no GitHub Release is needed.

For forks, update the repository manifest URL, each add-on's `config.yaml` homepage, README installation badges and support links directly.

## Reference and artwork

Packaging follows selected conventions from [Advanced SSH & Web Terminal v24.1.7](https://github.com/hassio-addons/app-ssh/tree/v24.1.7): a rootfs layout, pinned image inputs, Home Assistant/OCI metadata, configuration field descriptions and separate documentation files. Its terminal-specific privileges and S6 configuration do not apply here.

Preserve the upstream notices under `branding/` when redistributing Arcane artwork. Do not imply endorsement by Home Assistant, Arcane or the reference add-on's maintainers.
