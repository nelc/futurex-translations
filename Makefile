

.PHONY: .venv
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
		  atlas pull --repository=openedx/edx-platform --branch=open-release/palm.master --filter=ar \
		  		     conf/locale:translations-upstream/edx-platform/conf/locale


.PHONY: pull_and_replace
pull_and_replace: pull replace
