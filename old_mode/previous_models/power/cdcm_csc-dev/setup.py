"""CDCM models for the Cooling-Systems Cascade Scenario

Author:
    R Murali Krishnan
    
Date:
    09.13.2023
    
"""


from setuptools import setup, find_packages


__version__ = "0.2.0"


with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    _license = f.read()

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f]

setup(
    name="cdcm_csc",
    version=__version__,
    description="CDCM models for RETHi's Cooling-Systems Cascade scenario",
    author="R Murali Krishnan, Rashi Jain",
    author_email="mrajase@purdue.edu, jain356@purdue.edu",
    packages=find_packages(exclude=["tests*", "documentation"]),
    python_requires=">=3.8",
    license=_license,
    install_requires=requirements,
)
