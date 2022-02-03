from setuptools import setup, find_packages

setup(
    name='bpmsim',
    version='0.1',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='A business process simulation package',
    long_description=open('README.md').read(),
    install_requires=['simpy','numpy','scipy','matplotlib','xlsxwriter'],
    url='https://github.ugent.be/MIS/ProcessSimPython',
    author='Droomelot De Gendt',
    author_email='droomelot_degendt@hotmail.com'
)