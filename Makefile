all: build

build:
	python setup.py build

clean:
	python setup.py clean --all
	rm -rf build dist

install: 
	python setup.py install_test
	python setup.py install

test: clean
	cd src && py.test -n 1 --runslow --runperf

build_egg: build
	python setup.py bdist_egg

build_packages: build
	python setup.py bdist_rpm

register: build
	pip install --upgrade pip
	pip install --upgrade setuptools
	pip install wheel
	python setup.py bdist_egg bdist_wheel sdist upload -r internal


