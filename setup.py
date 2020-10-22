import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="szyfrow",
    version="0.0.6",
    author="Neil Smith",
    author_email="neil.szyfrow@njae.me.uk",
    description="Tools for using and breaking simple ciphers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NeilNjae/szyfrow",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    include_package_data=True,
)
