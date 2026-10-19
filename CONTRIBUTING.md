# Contributing

Issues and pull requests are welcome. For bugs, include the add-on version, CPU architecture, Home Assistant version, reproduction steps and logs with credentials removed.

## Repository layout

- `arcane_edge_agent/`: Monitor's local image build, startup script and fixed Docker API policy.
- `arcane_edge_agent_full/`: Full Access configuration using Arcane's official image.
- `tools/`: configuration checks, image build retries and Docker integration tests.
- `.github/workflows/validate.yml`: CI validation.

Each add-on has its own README, setup documentation, changelog, translations, icon and logo. JSON manifests are supported by Home Assistant alongside YAML.

Monitor uses Docker's init (`init: true`) and supervises its two processes in its startup script. It does not use S6. Full Access keeps `legacy: true` to pass configuration options to the official image. Neither agent needs host networking, exposed host ports or Supervisor API permissions.

## Local validation

```sh
sh -n arcane_edge_agent/rootfs/usr/local/bin/run-monitor
shellcheck arcane_edge_agent/rootfs/usr/local/bin/run-monitor
python3 tools/check_policy.py
python3 -m unittest discover -s tools -p test_build_image.py
python3 tools/test_proxy.py
```

The integration test requires a running Docker daemon. It builds Monitor and tests the actual proxy with a fake Docker socket, then verifies unprivileged startup, shutdown and the permission guard. The real host Docker socket is never mounted into test containers. Temporary test containers and volumes are removed afterward; the built test image remains cached.

CI authenticates to GHCR with a read-only job token and retries explicit registry rate-limit failures. Other build failures still fail immediately. Keep these checks intact when changing startup or access policy.

For changes to Docker access, verify both allowed monitoring requests and blocked write/file-download requests. Never broaden the allowlist merely to remove an Arcane UI error. Test installation, pairing, persistence and backup/restore on Home Assistant OS before declaring a release stable.

## Publishing an update

1. Update the relevant add-on's configuration version and changelog.
2. For Monitor, also update the Dockerfile's default `BUILD_VERSION` when changing the package version. Its upstream Arcane and proxy tags are pinned separately.
3. Full Access uses the configuration version as its official image tag. Verify that tag exists; an arbitrary packaging suffix would point to a nonexistent image.
4. Run the relevant checks, commit and push to the branch users have installed.
5. Home Assistant discovers the new version when its store refreshes. Users update through Home Assistant; no GitHub Release is needed.

For forks, update repository links, installation badges and add-on homepages. `python3 tools/configure_repository.py https://github.com/OWNER/REPOSITORY` updates repository and add-on homepage metadata; README badge and support links must be adjusted separately.

## Reference and artwork

Packaging follows selected conventions from [Advanced SSH & Web Terminal v24.1.7](https://github.com/hassio-addons/app-ssh/tree/v24.1.7): a rootfs layout, pinned image inputs, Home Assistant/OCI metadata, configuration field descriptions and separate documentation files. Its terminal-specific privileges and S6 configuration do not apply here.

Preserve the upstream notices under `branding/` when redistributing Arcane artwork. Do not imply endorsement by Home Assistant, Arcane or the reference add-on's maintainers.
