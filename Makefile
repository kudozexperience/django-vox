.PHONY: flake8 test coverage translatable_strings update_translations

flake8:
	flake8 django_courier tests

isort:
	isort -rc django_courier tests

isort_check_only:
	isort -rc -c django_courier tests

test:
	DJANGO_SETTINGS_MODULE=tests.settings \
		python3 -m django test $${TEST_ARGS:-tests}

coverage:
	DJANGO_SETTINGS_MODULE=tests.settings \
		coverage3 run -m django test -v2 $${TEST_ARGS:-tests}
	coverage3 report
	coverage3 erase

