

.PHONY: .venv

RELEASE_BRANCH := "open-release/redwood.master"
LANGUAGES := "ar,fr_CA"

.venv:
	rm -rf .venv/
	python3 -m venv .venv/
	. .venv/bin/activate && pip install -r requirements.txt


.PHONY: replace
replace: .venv
	rm -rf translation-overrides translations
	. .venv/bin/activate && python scripts/reword_translations.py .


.PHONY: pull
pull: .venv
	rm -rf translations-upstream

	. .venv/bin/activate && \
		  atlas pull --branch=$(RELEASE_BRANCH) --filter=$(LANGUAGES) \
		  		     translations:translations-upstream


.PHONY: pull_and_replace
pull_and_replace: pull replace
