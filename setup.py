import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="grab-fork-from-libgen",
    version="1.3.3",
    author="Lamarcke",
    author_email="cassiolamarcksilvafreitas@gmail.com",
    description="A fork of grab-convert-from-libgen.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="libgen ebooks books api scraper",
    url="https://github.com/Lamarcke/grab-fork-from-libgen",
    packages=setuptools.find_packages(exclude=("tests",)),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "requests",
        "requests-html",
        "lxml"
    ]
)

