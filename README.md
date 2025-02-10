# FutureX Translations

Custom translations for the FutureX Open edX Platform. This is fork of the standard https://github.com/openedx/openedx-translations/ for FutureX LMS use.

## Edit the Reword List

Open `scripts/reword_list.csv` and edit the entries as provided by NELC:

 - english_word: The English word, used for reference and double check.
 - arabic_word: The Arabic translation needing replacement.
 - arabic_replacement: The new Arabic translation.
 - note: Optional field if notes are needed.

## Refresh translations overrides

To get a fresh copy of the translation files (currently Redwood) and replace them please do the following:

```shell
make pull_and_replace
```

## Directory Structure

- `translations-upstream`: The upstream unmodified copy will be placed e.g. `translations-upstream/edx-platform/conf/locale`.
- `translations`: This contains a combined version of both upstream with overridden entries replaced. This file is going to be used by Tutor as described in the section below.


## Using in Tutor
As of Redwood, this repository is ready to be used in Tutor directly without additional plugins by setting the following configuration in Tutor:

```yaml
ATLAS_REPOSITORY: nelc/futurex-translations
ATLAS_REVISION: open-release/redwood.master  # The branch changes based on the release name
```
