"""
This script provides functionality to merge translation files in both .po and .json formats.
It checks for existing files and merges new entries into them, preserving the original content.

It supports:
- Merging .po files: If a message ID (msgid) from the source file already exists in the destination file,
  an exception is raised.
- Merging .json files: The contents of the source JSON file are merged into the destination JSON file,
  with existing data in the destination updated by the source.

Usage:
    python merge_translations.py <source_file> <dest_file>

Arguments:
    source_file (str): Path to the source file to be merged (either .po or .json).
    dest_file (str): Path to the destination file where the source file will be merged.

Modules used:
    - polib: To handle .po files.
    - json: To handle .json files.
    - sys: To handle command-line arguments.

Exceptions:
    - Exception: Raised when merging a .po file if a msgid already exists in the destination file.
    - ValueError: Raised if the source file format is unsupported.
    - FileNotFoundError: Raised if the source or destination file does not exist for JSON files.
"""
import json
import sys
from typing import Union

import polib


def merge_po_file(source: str, dest: str) -> None:
    """
    Merges entries from a source .po file into a destination .po file.
    If an entry with the same msgid already exists in the destination file,
    an exception is raised.

    Args:
        source (str): The file path of the source .po file to merge from.
        dest (str): The file path of the destination .po file to merge into.

    Raises:
        Exception: If an entry with the same msgid already exists in the destination file.
    """
    dest_po = polib.pofile(dest)
    source_po = polib.pofile(source)

    for entry in source_po:
        existing_entry = dest_po.find(entry.msgid)

        if existing_entry:
            raise Exception(f"Invalid entry {entry.msgid}: the id already exists")

        dest_po.append(entry)

    dest_po.save(dest)


def merge_json_file(source: str, dest: str) -> None:
    """
    Merges the contents of a source JSON file into a destination JSON file.
    The destination file's existing data will be updated with the source data.

    Args:
        source (str): The file path of the source JSON file to merge from.
        dest (str): The file path of the destination JSON file to merge into.

    Raises:
        FileNotFoundError: If either the source or destination file does not exist.
    """
    with open(source, 'r', encoding='utf-8') as src_file:
        source_data = json.load(src_file)

    with open(dest, 'r+', encoding='utf-8') as dst_file:
        dest_data = json.load(dst_file)
        dest_data.update(source_data)
        dst_file.seek(0)
        json.dump(dest_data, dst_file, ensure_ascii=False, indent=2)
        dst_file.truncate()


def main() -> None:
    """
    Main function that accepts file paths as command-line arguments to merge
    a source file into a destination file. Supports both .po and .json file formats.

    The function checks the file extension of the source file and calls the
    appropriate merge function accordingly.

    Raises:
        ValueError: If the source file format is not supported.
    """
    source_file = sys.argv[1]
    dest_file = sys.argv[2]

    if source_file.endswith('.po'):
        print(f"Merging {source_file} into {dest_file}")
        merge_po_file(source_file, dest_file)
    elif source_file.endswith('.json'):
        print(f"Merging {source_file} into {dest_file}")
        merge_json_file(source_file, dest_file)
    else:
        raise ValueError(f"Unsupported file format for {source_file}")


if __name__ == '__main__':
    main()
