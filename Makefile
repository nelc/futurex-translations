
RELEASE_BRANCH := "open-release/redwood.master"
LANGUAGES := "ar,fr_CA"

.PHONY: pull_and_replace
pull_and_replace: pull replace custom_translations

.PHONY: recreate_venv
recreate_venv:
	rm -rf .venv/
	python3 -m venv .venv/
	. .venv/bin/activate && pip install -r requirements.txt
	cp requirements.txt .venv/requirements.txt

.PHONY: venv
venv:
	cmp --silent requirements.txt .venv/requirements.txt || make recreate_venv


.PHONY: replace
replace: venv
	rm -rf translations
	. .venv/bin/activate && python scripts/reword_translations.py .

.PHONY: custom_translations
custom_translations:
	cp -r custom-translations/* translations/
	 

.PHONY: pull
pull: venv
	rm -rf translations-upstream

	. .venv/bin/activate && \
		  atlas pull --branch=$(RELEASE_BRANCH) --filter=$(LANGUAGES) \
		  		     translations:translations-upstream

