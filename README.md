# FutureX Translations

Custom translations for the FutureX Open edX Platform.

## Edit the Reword List

Open `scripts/reword_list.csv` and edit the entries as provided by NELC:

 - english_word: The English word, used for reference and double check.
 - arabic_word: The Arabic translation needing replacement.
 - arabic_replacement: The new Arabic translation.
 - note: Optional field if notes are needed.

## Refresh translations overrides

To get a fresh copy of the translation files (currently Palm) and replace them please do the following:

```shell
make pull_and_replace
```

The upstream unmodified copy will be placed in `translations-upstream/edx-platform/conf/locale`.

The override files will be placed in `translation-overrides/edx-platform/conf/locale`. Add the `translation-overrides`
files to your build.
