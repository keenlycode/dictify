import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dictify",
    version="1.1.0",
    author="Nitipit Nontasuwan",
    author_email="nitipit@gmail.com",
    description="Python `dict` and `json` verification for mankind :)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nitipit/dictify",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
