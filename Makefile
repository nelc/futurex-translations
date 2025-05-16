
RELEASE_BRANCH := "open-release/redwood.master"
LANGUAGES := "ar,fr_CA"
EDX_PLATFORM_LANGUAGES := "ar,fr_CA,en"

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
	@find custom-translations -type f | while read file; do \
		relative_path=$${file#custom-translations/}; \
		dest="translations/$$relative_path"; \
		mkdir -p "$$(dirname $$dest)"; \
		if [ -f "$$dest" ]; then \
			python scripts/merge_custom_translations.py "$$file" "$$dest"; \
		else \
			echo "Copying $$file to $$dest"; \
			cp "$$file" "$$dest"; \
		fi; \
	done


.PHONY: pull
pull: venv
	rm -rf translations-upstream

	. .venv/bin/activate && \
		  atlas pull --branch=$(RELEASE_BRANCH) --filter=$(LANGUAGES) \
		  		     translations:translations-upstream


	. .venv/bin/activate && \
		  atlas pull --branch=$(RELEASE_BRANCH) --filter=$(EDX_PLATFORM_LANGUAGES) \
		  		     translations/edx-platform:translations-upstream/edx-platform
