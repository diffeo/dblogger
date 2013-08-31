clean:
	rm -rf build dist

install: 
	python setup.py clean --all
	python setup.py install

test: clean
	python setup.py install_test > /dev/null
	cd src && py.test -n 3 --runslow --runperf

build_eggs: build
	python setup.py bdist_egg

build_packages: build_eggs
	python setup.py bdist_rpm

register: build
	python setup.py register sdist upload -r pypi


