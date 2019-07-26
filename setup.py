from setuptools import setup

setup(
   name='EnergyMarketTools',
   version='0.1',
   description='A collection of energy-market tools that leverate the US DOE EIA API',
   author='David Tew',
   author_email='davetew@alum.mit.edu',
   packages=['EnergyMarketTools'],  #same as name
   install_requires=['numpy', 'matplotlib','pandas','requests'], #external packages as dependencies
)
