
RELEASE_BRANCH := "open-release/redwood.master"
LANGUAGES := "ar,id,fr_CA"
EDX_PLATFORM_LANGUAGES := "$(LANGUAGES),en"
# <upstream code>:<code the platform asks for>. Upstream only ships French as fr_CA; see scripts/alias_language.py.
LANGUAGE_ALIASES := fr_CA:fr

.PHONY: pull_and_replace
pull_and_replace: pull replace custom_translations alias_languages

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
	@find custom-translations -type f | while read file; do \
		relative_path=$${file#custom-translations/}; \
		dest="translations/$$relative_path"; \
		mkdir -p "$$(dirname $$dest)"; \
		if [ -f "$$dest" ]; then \
			. .venv/bin/activate && python scripts/merge_custom_translations.py --source "$$file" --destination "$$dest"; \
		else \
			echo "Copying $$file to $$dest"; \
			cp "$$file" "$$dest"; \
		fi; \
	done


.PHONY: alias_languages
alias_languages: venv
	. .venv/bin/activate && python scripts/alias_language.py . $(LANGUAGE_ALIASES)


.PHONY: pull
pull: venv
	rm -rf translations-upstream

	. .venv/bin/activate && \
		  atlas pull --branch=$(RELEASE_BRANCH) --filter=$(LANGUAGES) \
		  		     translations:translations-upstream


	. .venv/bin/activate && \
		  atlas pull --branch=$(RELEASE_BRANCH) --filter=$(EDX_PLATFORM_LANGUAGES) \
		  		     translations/edx-platform:translations-upstream/edx-platform
