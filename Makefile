.PHONY: test deps docs build shell clean

all: env deps build test docs

deps:
	./env/bin/pip install -q -r 'test-requirements.txt'
	./env/bin/pip install -q -r 'requirements.txt'

env:
	virtualenv --distribute env

shell:
	./env/bin/ipython

build:
	./env/bin/pip install -e .

install:
	pip install -U --user -e .

test:
	./env/bin/flake8
	./env/bin/py.test -v

docs:
	./env/bin/webfriend --generate-docs > docs/commands.md

clean-cache:
	-rm -rf build dist
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

clean-build:
	-rm -rf *.egg-info build dist

clean: clean-cache clean-build
	-rm -rf env

package-build: clean-build
	python setup.py sdist bdist_wheel

package-sign:
	cd dist && gpg \
		--local-user 6A116E6B0F678FA5 \
		--detach-sign \
		--armor \
		--yes *.tar.gz

package-push:
	./env/bin/twine upload \
		--repository pypi \
		--skip-existing dist/*

package: package-build package-sign package-push clean-cache
