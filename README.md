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

## Directory Structure

- `translations-upstream`: The upstream unmodified copy will be placed e.g. `translations-upstream/edx-platform/conf/locale`.
- `translation-overrides`: The override-only files will be placed e.g. `translation-overrides/edx-platform/conf/locale`. The `translation-overrides`
can be appended to `LOCALE_PATHS` similar to themes translations.
- `translations`: This contains a combined version of both upstream with overridden entries replaced. This directory can be used directly via `atlas pull --repository=nelc/futurex-translations` during Docker builds in Redwood release and newer.
