import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="grab_from_libgen-willeyers", # Replace with your own username
    version="0.1.0",
    author="Will Meyers",
    author_email="will@willmeyers.net",
    description="An easy API for searching and downloading books from Libgen.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/willmeyers/grab-from-libgen",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)

