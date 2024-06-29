from setuptools import setup, find_packages

setup(
    name='electricity_data_fetching_tr',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'requests',
        'pandas',
        'forex-python',
        'workalendar',
    ],
    author='Rojen Arda Şeşen',
    author_email='sesen19@itu.edu.tr',
    description='Uses the EPIAS API to fetch electricity data for Turkey. The package also cleans and structures the data to be used in forecasting models.',
    license='GPL-3.0',
    keywords='electricity data_fetching ',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
    url='https://github.com/rojenarda/electricity_data_fetching_tr'
)