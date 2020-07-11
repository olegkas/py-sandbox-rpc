#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Created Date: 2020-04-16 15:45:59
# Author: Oleg Kashaev
# Contact: oleg.kashaev.4@gmail.com
# -----
# MIT License
# Copyright (c) 2020 Oleg Kashaev

import setuptools
import sys

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("VERSION", "r") as fh:
    version = fh.read().strip()

if 'sdist' in sys.argv:
    ver = [int(s.strip()) for s in version.split(".")]
    ver[-1] += 1
    version = ".".join([str(d) for d in ver])
    with open("VERSION", "w") as fh:
        fh.write(version)

setuptools.setup(
    name="sandbox-rpc",
    version=version,
    author="Oleg Kashaev",
    author_email="oleg.kashaev.4@gmail.com",
    description="Python rpc decorator converting a python function to RPC" +
                " & Flask base namespace to execute rpc remotely",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/olegkas4/py-sandbox-rpc",
    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    data_files=[
        ('', ['VERSION'])
    ],
    python_requires='>=3.8',
    install_requires=[
        'Werkzeug==0.16.1',
        'Flask==1.1.2',
        'flask-restplus==0.13.0',
        'requests==2.23.0',
        'uWSGI==2.0.18',
        'cryptography==2.9.2'
    ]
)