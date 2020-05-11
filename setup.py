import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bank2ynab",
    version="1.2dev",
    author="https://github.com/bank2ynab/bank2ynab/graphs/contributors",
    author_email="torben@g-b.dk",
    description="Easily convert and import your bank's statements into YNAB.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bank2ynab/bank2ynab",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
