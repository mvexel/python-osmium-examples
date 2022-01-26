from setuptools import setup

setup(
    name='python-osmium-examples',
    version='0.1.0',
    py_modules=['python-osmium-examples'],
    install_requires=[
        'Click',
        'osmium'
    ],
    entry_points={
        'console_scripts': [
            'count_highway_mappers = highway_mappers:cli',
        ],
    },
)
