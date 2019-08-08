'''
Look up packaging instructions from Serious Python to see if anything has changed for Python 3
'''

from setuptools import setup

#this should be pretty detailed; generate from function definitions (i.e. Serious Python)
def readme():
	with open('README.md') as f:
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
	  packages=['aspace_tools'],
	  install_requires=['requests', 'paramiko', 'pymysql', 'sshtunnel', 'pandas', 'bs4', 'yaml', 'git+https://github.com/username/repo.git'],
	  include_package_data=True,
	  zip_safe=False)


#NEED TO ADD A REQUIREMENT TO INSTALL UTILITIES