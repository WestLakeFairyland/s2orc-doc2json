#!/usr/bin/python
import setuptools

setuptools.setup(
    name='pdf2json',
    version='0.1',
    packages=setuptools.find_packages(),
    install_requires=[
    ],
    tests_require=[
    ],
    zip_safe=False,
    test_suite='py.test',
    entry_points='',
)

setuptools.setup(
    name='grobid',
    version='0.1',
    packages=setuptools.find_packages(),
    install_requires=[
    ],
    tests_require=[
    ],
    zip_safe=False,
    test_suite='py.test',
    entry_points='',
)