.PHONY: flake8 test coverage

flake8:
	flake8 django_courier tests

isort:
	isort -rc django_courier tests

isort_check_only:
	isort -rc -c django_courier tests

test:
	pytest tests/

demo:
	DJANGO_SETTINGS_MODULE=tests.settings \
	PYTHONPATH="${PYTHONPATH}:." \
	django-admin runserver

coverage:
	pytest --cov=django_courier tests/

