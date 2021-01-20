from setuptools import setup

setup(
   name='EnergyMarketTools',
   version='0.1',
   description='A collection of energy-market tools that leverate the US DOE EIA & FRED APIs',
   author='David Tew',
   author_email='davetew@alum.mit.edu',
   url='https://github.com/davetew/EnergyMarketTools',
   packages=setuptools.find_packages(),  #same as name
   install_requires=['numpy', 'matplotlib','pandas','requests','fredapi'], #external packages as dependencies
)
