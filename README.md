# FutureX Translations

Custom translations for the FutureX Open edX Platform. This is fork of the standard https://github.com/openedx/openedx-translations/ for FutureX LMS use.

## Edit the Reword List

Open `scripts/reword_list.csv` and edit the entries as provided by NELC:

 - english_word: The English word, used for reference and double check.
 - arabic_word: The Arabic translation needing replacement.
 - arabic_replacement: The new Arabic translation.
 - note: Optional field if notes are needed.

## Refresh Translations

To get a fresh copy of the translation files (currently Redwood) and replace them please do the following:

```shell
make pull_and_replace
```

## Adding Custom Translations
- Add the translation file manually into this repository e.g.  `translations-custom/frontend-essentials/src/i18n/messages/ar.json`.
- Run `make pull_and_replace` to add the custom translations into the `translations/` directory.
- Create a pull request and merge in the release branch e.g. `open-release/redwood.master`
- Update the `pull_translations` program in the `Makefile` of the repository e.g. Frontend Learning MFE.
- Re-deploy the Micro-frontend or the Microservice to fetch the latest translations.


## Directory Structure

- `translations-upstream`: The upstream unmodified copy will be placed e.g. `translations-upstream/edx-platform/conf/locale`.
- `translations-custom`: FutureX-specific translatiosn goes here e.g. `translations-custom/frontend-essentials/src/i18n/messages/ar.json`.
- `translations`: This contains a final version of both upstream with overridden entries replaced. This directory is going to be used by Tutor as described in the section below.

## Using in Tutor
As of Redwood, this repository is ready to be used in Tutor directly without additional plugins by setting the following configuration in Tutor:

```yaml
ATLAS_REPOSITORY: nelc/futurex-translations
ATLAS_REVISION: open-release/redwood.master  # The branch changes based on the release name
```
