import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="szyfrow",
    version="0.0.7",
    author="Neil Smith",
    author_email="neil.szyfrow@njae.me.uk",
    description="Tools for using and breaking simple ciphers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NeilNjae/szyfrow",
    project_urls={
        "Documentation": "https://neilnjae.github.io/szyfrow/szyfrow/index.html",
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Natural Language :: English",
        "Topic :: Security :: Cryptography",
    ],
    python_requires='>=3.7',
    install_requires=[],
    include_package_data=True,
    setup_requires=['pytest-runner', 'numpy'],
    tests_require=['pytest'],
    test_suite="tests",
)
