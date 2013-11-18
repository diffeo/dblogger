all: build

build:
	python setup.py build

clean:
	python setup.py clean --all
	rm -rf build dist

install: clean
	python setup.py install_test
	python setup.py install

test: install
	python setup.py test

register: build
	pip install --upgrade pip
	pip install --upgrade setuptools
	pip install wheel
	python setup.py bdist_egg bdist_wheel sdist upload


