"""Setup DiscreteLatticeMech."""
import os
from distutils.core import setup


SETUP_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SETUP_DIR)

requirements_filepath = os.path.join(SETUP_DIR, 'requirements.txt')

DEPENDENCIES = []
if os.path.exists(requirements_filepath):
    for line in open(requirements_filepath):
        DEPENDENCIES.append(line.strip())

NAME = 'DiscreteLatticeMech'

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name=NAME,
    version='1.0.0',
    author='Nikos Karathanasopoulos',
    author_email='karathanasopoulosn@gmail.com',
    description='DiscreteLatticeMech',
    license='MIT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/nkarathan/DiscreteLatticeMech',
    packages=['DiscreteLatticeMech'],
    include_package_data=True,
    install_requires=DEPENDENCIES,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved",
        "Operating System :: OS Independent",
    ],
    zip_safe=False
)

