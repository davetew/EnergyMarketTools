from setuptools import setup

setup(
   name='Energy-Market-Tools',
   version='0.1',
   description='A collection of energy-market tools that leverate the US DOE EIA API',
   author='David Tew',
   author_email='davetew@alum.mit.edu',
   packages=['Energy-Market-Tools'],  #same as name
   install_requires=['numpy', 'matplotlib','pandas','requests'], #external packages as dependencies
)
