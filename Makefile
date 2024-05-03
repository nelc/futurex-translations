

.PHONY: .venv
.venv:
	rm -rf .venv/
	python3 -m venv .venv/
	. .venv/bin/activate && pip install -r requirements.txt

.PHONY: pull_and_replace
pull_and_replace: .venv
	rm -rf translations-upstream
	rm -rf translation-overrides

	. .venv/bin/activate && \
		  atlas pull --repository=openedx/edx-platform --branch=open-release/palm.master --filter=ar \
		  		     conf/locale:translations-upstream/edx-platform/conf/locale
	. .venv/bin/activate && python scripts/reword_translations.py .
