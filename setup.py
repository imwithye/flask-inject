"""
Flask-Inject
-------------

A micro dependency injection framework for Flask micro web framework :)
"""
from setuptools import setup

setup(
    name='Flask-Inject',
    version='1.1.0',
    url='https://github.com/imwithye/flask-inject',
    license='BSD',
    author='Ciel',
    author_email='imwithye@gmail.com',
    description='A micro dependency injection framework for Flask micro web framework :)',
    long_description=__doc__,
    py_modules=['flask_inject'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
