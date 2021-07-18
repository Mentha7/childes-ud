from setuptools import setup, find_namespace_packages

setup(
    name="chatconllu",
    version="0.0.1",
    packages=find_namespace_packages(),
    entry_points={"console_scripts": ["chatconllu=cli:main"]},
)
