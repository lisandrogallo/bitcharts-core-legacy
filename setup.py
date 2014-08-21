# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='bitcharts-core',
    version='0.2.0',
    author='Lisandro Gallo',
    author_email = 'liso@riseup.net',
    description = ('Core and scripts used on http://bitcharts.io'),
    install_requires=[
        'Flask==0.10.1',
        'Flask-SQLAlchemy==1.0',
        'Flask-Script==2.0.5',
        ],
    keywords='',
    license = 'AGPL',
    url = 'http://bitcharts.io',
    packages=['bitcharts'],
    # long_description=read('README'),
    classifiers=[],
    )
