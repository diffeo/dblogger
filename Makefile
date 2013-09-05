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
	cd src && py.test -n 3 --runslow --runperf

build_egg: build
	python setup.py bdist_egg

build_packages: build
	python setup.py bdist_rpm

register: build
	python setup.py register sdist upload -r internal


