from setuptools import setup


requirements = [l.strip() for l in open('requirements.txt').readlines()]

# To set __version__
__version__ = 'unknown'
execfile('ua_utils/_version.py')

setup(
    name='ua-api-utils',
    url='https://github.com/urbanairship/ua-api-utils',
    version=__version__,
    license='APLv2',
    author='Michael Schurter',
    author_email='schmichael@urbanairship.com',
    description="Utilities for working with Urban Airship's APIs",
    packages=['ua_utils'],
    entry_points={
        'console_scripts': [
            'ua=ua_utils.cli:main',
        ],
    },
    install_requires=requirements,
    classifiers=['License :: OSI Approved :: Apache Software License'],
    # It might actually be zip-safe, I just hate eggs. File an issue or pull
    # request if you want zip_safe=True
    zip_safe=False
)
