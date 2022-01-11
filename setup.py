import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gnucash-uk-corptax",
    version="1.2.0",
    author="Cybermaggedon",
    author_email="mark@cyberapocalypse.co.uk",
    description="UK HMRC Corporation Tax client for GnuCash users",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cybermaggedon/gnucash-uk-corptax",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    download_url = "https://github.com/cybermaggedon/gnucash-uk-corptax/archive/refs/tags/v1.2.0.tar.gz",
    install_requires=[
        'aiohttp',
        'py-dmidecode',
        'requests',
        'ixbrl-parse'
    ],
    scripts=[
        "scripts/gnucash-uk-corptax",
        "scripts/corptax-test-service"
    ]
)
