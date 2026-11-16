"""Generate release entries from Renovate's manifest and Dockerfile changes."""
import re
import subprocess
from pathlib import Path

ADDONS = ('arcane_edge_agent', 'arcane_edge_agent_full')


def read(ref, path):
    return subprocess.check_output(['git', 'show', f'{ref}:{path}'], text=True)


def version(text):
    return re.search(r'^version: [\"\']?(\d+\.\d+\.\d+-\d+)', text, re.M)[1]


def update_changelog(changelog, release, notes):
    heading = f'## {release}\n'
    if heading in changelog:
        return changelog
    position = changelog.index('\n## ')
    return changelog[:position] + f'\n## {release}\n\n' + ''.join(f'- {note}\n' for note in notes) + changelog[position:]


def main():
    for addon in ADDONS:
        old = version(read('base', f'{addon}/config.yaml'))
        new = version(read('head', f'{addon}/config.yaml'))
        path = Path(addon) / 'CHANGELOG.md'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(read('head', str(path)))
        if old == new:
            continue
        old_upstream, new_upstream = old.split('-')[0], new.split('-')[0]
        notes = []
        if old_upstream != new_upstream:
            notes.append(f'Update Arcane from v{old_upstream} to v{new_upstream}.')
        else:
            notes.append('Update runtime dependencies and increment the packaging revision.')
        path.write_text(update_changelog(read('head', str(path)), new, notes))


if __name__ == '__main__':
    main()
