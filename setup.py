#!/usr/bin/env python3

from setuptools import setup, find_packages
from catapult.version import __version__


def requirements():
    requirements_list = []

    with open('requirements.txt') as requirements:
        for install in requirements:
            requirements_list.append(install.strip())

    return requirements_list


packages = find_packages(exclude=['tests*'])

setup(name='catapult3',
      version=__version__,
      author='Artemiy Pulyavin',
      author_email='artemiy@pulyavin.ru',
      license='LGPLv3',
      keywords='deploy',
      description='Catapult - DevOps Deployment System',
      packages=packages,
      install_requires=requirements(),
      include_package_data=True,
      scripts=['bin/catapult'],
      zip_safe=False,
      )
