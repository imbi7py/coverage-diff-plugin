from setuptools import setup, find_packages

setup(
    name="diff_coverage",
    packages=find_packages(),
    install_requires=[
        "attrs",
        "coverage",
        "unidiff",
    ]
)
