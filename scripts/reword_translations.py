"""
Reword translations.

This scripts reads a root directory and presumes the following structure:

 - translations-upstream/  # The main unmodified translations structure similar to the `openedx/openedx-translations:translations` directory.
"""

from typing import List

import subprocess
import sys
from pathlib import Path
import csv
import re
from dataclasses import dataclass


class ValidationError(RuntimeError):
    pass


@dataclass
class Reword:
    """
    Reword entry from the reword_list.csv file.
    """
    english_word: str
    arabic_word: str
    arabic_replacement: str
    note: str

    def replace_words(self, s) -> str:
        """
        Strictly replace words without crossing word boundaries.
        """
        return replace_words(s, self.arabic_word, self.arabic_replacement)

    def is_arabic_strict_match(self, file_path: str) -> bool:
        """
        Strictly match against self.arabic_word without crossing word boundaries.
        """
        with open(file_path) as fr:
            for line in fr:
                if contains_word(line, self.arabic_word):
                    return True

    def reword_file(self, lines: List[str]) -> List[str]:
        new_content_lines = [
            self.replace_words(line)
            for line in lines
        ]

        return new_content_lines


def replace_words(s, word, replacement) -> str:
    return re.sub(
        pattern=rf'\b{word}\b',
        repl=replacement,
        string=s,
        flags=re.IGNORECASE,
    )


def contains_word(s, word):
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


def create_overrides_po_file(
    source: Path,
    combined_dest: Path,
    reword_list: List[Reword],
):
    print(f'## Rewording: {source}  ##')

    with source.open() as source_f:
        lines = source_f.readlines()
        for reword in reword_list:
            lines = reword.reword_file(lines)

        with combined_dest.open('w') as combined_dest_f:
            combined_dest_f.writelines(lines)


def verify_course_translation(path: Path):
    """
    Special check: Ensure the file don't contain the unneeded word `course`.
    """
    unneeded_course_word = 'مساق'
    with open(path) as f:
        if unneeded_course_word in f.read():
            subprocess.call(['grep', '--before=4', '--after=2', unneeded_course_word, path])
            raise ValidationError(
                f'Error: The "{path}" file has an unneeded translation for the '
                f'word "course" as "{unneeded_course_word}".'
            )


def main(repo_root, *_argv):
    repo_root = Path(repo_root)
    reword_csv_file = repo_root / 'scripts/reword_list.csv'

    reword_list = get_reword_list(reword_csv_file)

    upstream_translations_dir = repo_root / 'translations-upstream'
    updated_translations_dir = repo_root / 'translations'

    translation_paths = get_translation_relative_paths(upstream_translations_dir)

    for translation_path in translation_paths:
        combined_dest = updated_translations_dir / translation_path
        mk_parents(combined_dest)

        create_overrides_po_file(
            source=upstream_translations_dir / translation_path,
            combined_dest=combined_dest,
            reword_list=reword_list,
        )

        verify_course_translation(path=combined_dest)

    print('Finished rewording successfully')


if __name__ == '__main__':
    main(*sys.argv[1:])
