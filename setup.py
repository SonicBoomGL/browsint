from setuptools import find_packages, setup

setup(
    name="browsint",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "beautifulsoup4",
        "colorama",
        "requests",
        "tabulate",
    ],
)
