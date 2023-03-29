from setuptools import setup, find_packages

setup(
    name='python-osmium-examples',
    version='0.1.2',
    py_modules=['python-osmium-examples'],
    install_requires=[
        'Click',
        'osmium',
        'pandas',
        'shapely',
        'matplotlib'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'count_highway_mappers = highway_mapper.highway_mapper:cli',
            'plot_admin_level_areas = admin_area_plotter.admin_area_plotter:cli',
        ],
    },
)
