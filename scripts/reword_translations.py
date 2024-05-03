"""
Reword translations.

This scripts reads a root directory and presumes the following structure:

 - translations-upstream/  # The main unmodified translations structure similar to the `openedx/openedx-translations:translations` directory.
 - translation-overrides/  # The same structure of the above files, but it contains only overridden files.
"""

import sys
from pathlib import Path
import csv
import polib
import re
from dataclasses import dataclass


@dataclass
class Reword:
    """
    Reword entry from the reword_list.csv file.
    """
    english_word: str
    arabic_word: str
    arabic_replacement: str
    note: str

    def is_match(self, entry: polib.POEntry):
        return contains_words(entry.msgid, self.english_word)

    def replace_words(self, s):
        return replace_words(s, self.arabic_word, self.arabic_replacement)

    def reword_entry(self, entry: polib.POEntry):
        entry.msgstr = self.replace_words(entry.msgstr)

        for index in sorted(entry.msgstr_plural.keys()):
            entry.msgstr_plural[index] = self.replace_words(entry.msgstr_plural[index])

        return entry


def replace_words(s, word, replacement):
    return re.sub(
        pattern=rf'\b{word}\b',
        repl=replacement,
        string=s,
        flags=re.IGNORECASE,
    )


def contains_words(s, word):
    return re.search(pattern=rf'\b{word}\b', string=s, flags=re.IGNORECASE)


def mk_parents(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)

def get_translation_relative_paths(root_dir: Path):
    return [
        path.relative_to(root_dir)
        for path in root_dir.rglob('*.po')
    ]


def get_reword_list(reword_csv_file: Path):
    with open(reword_csv_file) as f:
        return [
            Reword(**row)
            for row in csv.DictReader(f)
        ]


def create_overrides_po_file(source: Path, dest: Path, reword_list: list):
    source_po = polib.pofile(source)
    dest_po = polib.POFile()
    dest_po.metadata = source_po.metadata

    for entry in source_po.translated_entries():
        has_reword = False

        for reword in reword_list:
            if reword.is_match(entry):
                has_reword = True
                entry = reword.reword_entry(entry)

        if has_reword:
            dest_po.append(entry)

    dest_po.save(dest)


def main(repo_root, *_argv):
    repo_root = Path(repo_root)
    reword_csv_file = repo_root / 'scripts/reword_list.csv'

    reword_list = get_reword_list(reword_csv_file)

    upstream_translations_dir = repo_root / 'translations-upstream'
    translation_overrides_dir = repo_root / 'translation-overrides'

    translation_paths = get_translation_relative_paths(upstream_translations_dir)

    for translation_path in translation_paths:
        dest = translation_overrides_dir / translation_path
        mk_parents(dest)

        create_overrides_po_file(
            source=upstream_translations_dir / translation_path,
            dest=dest,
            reword_list=reword_list,
        )


if __name__ == '__main__':
    main(*sys.argv[1:])
