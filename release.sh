#!/bin/bash

set -e

if [[ -n "$VIRTUAL_ENV" ]] ; then
	echo "Deactivate your virtualenv first!"
	exit 1
fi

tox

python3 -m virtualenv --python python3 venv3

for v in 3 ; do
	venv="venv${v}"
	python="$venv/bin/python${v}"
	pip="$venv/bin/pip${v}"

	$pip install --upgrade pip wheel -e .
	$python setup.py bdist_wheel upload
	rm -rf "$venv"
done

rm -rf build
