from setuptools import find_packages, setup

setup(
    name="browsint",
    version="1.0.0b",
    description="Web Intelligence & OSINT Collection Tool",
    author="Gianluca Bassani",
    url="https://github.com/SonicBoomGL/browsint",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "beautifulsoup4",
        "colorama",
        "requests",
        "tabulate",
        "validators",
        "phonenumbers",
        "dnspython",
        "shodan",
        "pdfkit",
        "pandas",
        "ipwhois",
        "python-dotenv",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
