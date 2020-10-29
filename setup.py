#! /usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='svgprestools',
    license="MIT",
    version="0.1",
    description='A collection of tools for generating svg images for presentations.',
    url='https://github.com/CD3/txt2svg',
    author='C.D. Clark III',
    packages=find_packages(),
    install_requires=['click','lxml'],
    entry_points='''
    [console_scripts]
    txt2svg=svgprestools.scripts:txt2svg
    svgmontage=svgprestools.scripts:svgmontage
    write2sozi=svgprestools.scripts:write2sozi
    update-sozi-presentation=svgprestools.scripts:updateSoziPresentation
    ''',
)
