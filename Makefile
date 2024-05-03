

.PHONY := .venv/
.venv/:
	rm -rf .venv/
	python3 -m venv .venv/
	. .venv/bin/activate &&
		pip install -r requirements.txt


.PHONY := pull_and_replace
pull_and_replace: .venv/
	rm -rf release-translations
	mkdir -p translations/edx-platform/conf/locale

	. .venv/bin/activate && \
		  atlas pull --repository=openedx/edx-platform --branch=open-release/palm.master --filter=ar \
		  		     conf/locale:release-translations/edx-platform/conf/locale
	. .venv/bin/activate && python scripts/reword_translations.py release-translations translations
