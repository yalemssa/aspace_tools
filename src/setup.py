'''
Look up packaging instructions from Serious Python to see if anything has changed for Python 3
'''

from setuptools import setup, find_packages

#this should be pretty detailed; generate from function definitions (i.e. Serious Python)
def readme():
	with open('/Users/aliciadetelich/Dropbox/git/aspace_tools/docs/README.md') as f:
		return f.read()

setup(name='aspace_tools',
	  version='0.0.1',
	  description='Scripts for interacting with the ArchivesSpace database and API',
	  long_description=readme(),
	  #url='https://github.com/ucancallmealicia/utilities',
      license='MIT',
	  author='Alicia Detelich',
	  author_email='adetelich@gmail.com',
      classifiers=[
          'Development Status : : Alpha',
          'License :: OSI Approved :: MIT License'
          'Programming Language :: Python :: 3.6',
          'Natural Language :: English',
          'Operating System :: OS Independent'
          ],
	  packages=find_packages(),
	  install_requires=['requests', 'lxml', 'tqdm', 'pymssql', 'pandas', 'decorator', 'pyyaml', 'rich'],
	  include_package_data=True,
	  zip_safe=False)
