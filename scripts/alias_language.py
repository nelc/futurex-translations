#!/usr/bin/env python3
"""
Alias one language code to another inside `translations/`.

Why: upstream only ships French as `fr_CA`, but the platform and the micro-frontends look a language
up by the code the learner picked (`fr`). The Django side needs a `conf/locale/fr/` directory and
the MFE side needs a `fr.json` (which `intl-imports` turns into the `fr` message key); with only
`fr_CA` both fall back to English.

For every `<src>` directory (Django `locale/<src>/`) and every `<src>.json` file found under
`<root>/translations`, this writes the same content next to it under `<dst>`.
`.po` files only get their `Language:` header rewritten.

Rules:
  - Run it AFTER `replace` and `custom_translations`, so rewording and custom strings reach the alias.
  - Fails loudly (exit 1) when a pair finds no source, or when an existing `<dst>` differs from what
    would be written (e.g. upstream started shipping a real `<dst>` catalogue).
  - Idempotent: a second run over the same tree changes nothing.

Usage:
    python scripts/alias_language.py <repo-root> fr_CA:fr [src:dst ...]
"""
import json
import sys
from pathlib import Path

SKIP_DIRS = {'.git', '.venv', 'node_modules'}


def rewrite(src_file: Path, src: str, dst: str) -> bytes:
    data = src_file.read_bytes()
    if src_file.suffix == '.po':
        data = data.replace(f'"Language: {src}\\n"'.encode(), f'"Language: {dst}\\n"'.encode())
    elif src_file.suffix == '.json':
        json.loads(data)  # refuse to propagate a broken catalogue
    return data


def write_if_changed(dest: Path, data: bytes) -> bool:
    if dest.exists():
        if dest.read_bytes() == data:
            return False
        raise SystemExit(
            f'ERROR: {dest} already exists with different content; refusing to overwrite. '
            'Re-run the full `make pull_and_replace` (it rebuilds translations/ first), '
            'or remove the file if it is a stale alias.'
        )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return True


def alias(translations: Path, src: str, dst: str) -> int:
    sources = []
    for path in sorted(translations.rglob('*')):
        if SKIP_DIRS & set(path.parts):
            continue
        if path.is_dir() and path.name == src:
            sources += [(f, dst_dir_file(f, path, src, dst)) for f in sorted(path.rglob('*')) if f.is_file()]
        elif path.is_file() and path.name == f'{src}.json':
            sources.append((path, path.with_name(f'{dst}.json')))

    if not sources:
        raise SystemExit(f'ERROR: no `{src}` catalogue found under {translations}; nothing to alias to `{dst}`.')

    written = sum(write_if_changed(dest, rewrite(source, src, dst)) for source, dest in sources)
    print(f'alias {src} -> {dst}: {len(sources)} files ({written} written, {len(sources) - written} unchanged)')
    return len(sources)


def dst_dir_file(file: Path, src_dir: Path, src: str, dst: str) -> Path:
    return src_dir.with_name(dst) / file.relative_to(src_dir)


def main(root, *pairs):
    if not pairs:
        raise SystemExit(__doc__)
    translations = Path(root) / 'translations'
    if not translations.is_dir():
        raise SystemExit(f'ERROR: {translations} is not a directory.')
    for pair in pairs:
        src, _, dst = pair.partition(':')
        if not src or not dst or src == dst:
            raise SystemExit(f'ERROR: bad pair {pair!r}; expected <src>:<dst> with different codes.')
        alias(translations, src, dst)


if __name__ == '__main__':
    main(*sys.argv[1:])
