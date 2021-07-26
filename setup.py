import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hg-cache",
    version="0.1",
    author="Vladimir Looze",
    author_email="woldemar@mimas.ru",
    description="Mercurial extension for caching remote repositories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/trassir/hg-cache",
    packages=setuptools.find_packages(where='src'),
    # When your source code is in a subdirectory under the project root, e.g.
    # `src/`, it is necessary to specify the `package_dir` argument.
    package_dir={'': 'src'},
    license="GNU General Public License v3 (GPLv3)",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Version Control :: Mercurial",
        "Intended Audience :: Developers"
    ],
    python_requires=">=3.6",
    install_requires=[
        "mercurial>=5.8"
    ]
)
