"""
Reword translations.

This scripts reads a root directory and presumes the following structure:

 - translations-upstream/  # The main unmodified translations structure similar to the `openedx/openedx-translations:translations` directory.
 - translation-overrides/  # The same structure of the above files, but it contains only overridden files.
"""
import subprocess
import sys
from pathlib import Path
import csv
import polib
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

    def is_english_loose_match(self, entry: polib.POEntry) -> bool:
        """
        Case-insensitive check for a word without checking for word boundary.
        """
        return self.english_word.lower() in entry.msgid.lower()

    def replace_words(self, s) -> str:
        """
        Strictly replace words without crossing word boundaries.
        """
        return replace_words(s, self.arabic_word, self.arabic_replacement)

    def is_arabic_strict_match(self, entry: polib.POEntry) -> bool:
        """
        Strictly match against self.arabic_word without crossing word boundaries.
        """
        has_match = contains_word(entry.msgstr, self.arabic_word)

        for index in sorted(entry.msgstr_plural.keys()):
            has_match = has_match or contains_word(entry.msgstr_plural[index], self.arabic_word)

        return has_match

    def reword_entry(self, entry: polib.POEntry) -> polib.POEntry:
        entry.msgstr = self.replace_words(entry.msgstr)

        for index in sorted(entry.msgstr_plural.keys()):
            entry.msgstr_plural[index] = self.replace_words(entry.msgstr_plural[index])

        return entry


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
    overrides_dest: Path,
    combined_dest: Path,
    reword_list: list[Reword],
):
    source_po = polib.pofile(str(source))
    overrides_dest_po = polib.POFile()
    overrides_dest_po.metadata = source_po.metadata
    combined_dest_po = polib.POFile()
    combined_dest_po.metadata = source_po.metadata

    for entry in source_po.translated_entries():
        has_reword = False

        for reword in reword_list:
            if reword.is_english_loose_match(entry):
                has_reword = True
                entry = reword.reword_entry(entry)

        combined_dest_po.append(entry)
        if has_reword:
            overrides_dest_po.append(entry)

    overrides_dest_po.save(str(overrides_dest))
    combined_dest_po.save(str(combined_dest))


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


def verify_all_translations(path: Path, reword_list: list[Reword]):
    """
    Ensure the file don't contain the unneeded words.
    """
    po_file = polib.pofile(str(path))

    for entry in po_file.translated_entries():
        for reword in reword_list:
            if reword.is_arabic_strict_match(entry):
                raise ValidationError(
                    f'Error: The "{path}" file has the following reword entries unprocessed: "{reword.arabic_word}". \n'
                    f'       msgid: "{entry.msgid}". \n'
                    f'       msgstr: "{entry.msgstr}". \n'
                )


def main(repo_root, *_argv):
    repo_root = Path(repo_root)
    reword_csv_file = repo_root / 'scripts/reword_list.csv'

    reword_list = get_reword_list(reword_csv_file)

    upstream_translations_dir = repo_root / 'translations-upstream'
    translation_overrides_dir = repo_root / 'translation-overrides'
    updated_translations_dir = repo_root / 'translations'

    translation_paths = get_translation_relative_paths(upstream_translations_dir)

    for translation_path in translation_paths:
        overrides_dest = translation_overrides_dir / translation_path
        mk_parents(overrides_dest)
        combined_dest = updated_translations_dir / translation_path
        mk_parents(combined_dest)

        create_overrides_po_file(
            source=upstream_translations_dir / translation_path,
            overrides_dest=overrides_dest,
            combined_dest=combined_dest,
            reword_list=reword_list,
        )

        verify_course_translation(path=overrides_dest)
        verify_all_translations(path=overrides_dest, reword_list=reword_list)


if __name__ == '__main__':
    main(*sys.argv[1:])
