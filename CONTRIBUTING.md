# Contributing

Issues and pull requests are welcome. For bugs, include the add-on version, CPU architecture, Home Assistant version, reproduction steps and logs with credentials removed.

## Repository layout

- `arcane_edge_agent/`: Monitor's local image build, startup script and fixed Docker API policy.
- `arcane_edge_agent_full/`: Full Access image inheriting the pinned official Arcane image with only Home Assistant labels.
- `tests/`: configuration checks, Docker integration tests and their helpers.
- `.github/workflows/pipeline.yml`: reusable validation, tagging and releases.
- `.github/renovate.json`: image, action and Python dependency updates.

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

Both packages share one semantic release version, independent of the upstream Arcane tag. For a packaging change, increment both `config.yaml` versions and update the add-on changelogs. Supervisor supplies the image labels; no Dockerfile package version is needed.

Renovate groups runtime image updates and bumps both manifests with `bumpVersions`, including proxy-only or Alpine-only updates. Arcane stays pinned to the same upstream version in both Dockerfiles. CI checks that invariant without hardcoding a release, so future Renovate updates can pass. Non-major updates auto-merge after successful checks; major updates require review.

Enable the Renovate GitHub App for this repository and allow squash merging. Protect `main` with the two validation jobs as required checks. Renovate performs merges itself (`platformAutomerge: false`); no scheduled Renovate workflow or PAT is needed. GitHub Actions needs permission to create tags and releases via `GITHUB_TOKEN`.

The pipeline runs validation on native amd64 and aarch64 runners. After successful validation on `main`, it creates the package-version tag and generates GitHub release notes. Re-running the pipeline can finish a missing release for an existing tag. Home Assistant uses the manifests for update discovery; GitHub Releases provide notes, not images. Enable automatic updates separately in Home Assistant if wanted.

For forks, update the repository manifest URL, each add-on's `config.yaml` homepage, README installation badges and support links directly.

## Reference and artwork

Packaging follows selected conventions from [Advanced SSH & Web Terminal v24.1.7](https://github.com/hassio-addons/app-ssh/tree/v24.1.7): a rootfs layout, pinned image inputs, Supervisor-provided Home Assistant metadata, configuration field descriptions and separate documentation files. Its terminal-specific privileges and S6 configuration do not apply here.

Preserve the upstream notices under `branding/` when redistributing Arcane artwork. Do not imply endorsement by Home Assistant, Arcane or the reference add-on's maintainers.

Additional references: [Jellyfin packaging and Renovate](https://github.com/hassio-addons/app-jellyfin) and [ESPHome CI](https://github.com/esphome/esphome). The official Arcane runtime remains the Full Access base; Monitor retains only the extra filtering and privilege separation it needs.
