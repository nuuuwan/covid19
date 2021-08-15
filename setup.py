import setuptools

DIST_NAME = 'covid19'
version = '1.0.2'

setuptools.setup(
    name="%s-nuuuwan" % DIST_NAME,
    version=version,
    author="Nuwan I. Senaratna",
    author_email="nuuuwan@gmail.com",
    description="",
    long_description='',
    long_description_content_type="text/markdown",
    url="https://github.com/nuuuwan/%s" % DIST_NAME,
    project_urls={
        "Bug Tracker": "https://github.com/nuuuwan/%s/issues" % DIST_NAME,
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        'pycountry',
        'pypopulation',
        'utils-nuuuwan',
        'tablex-nuuuwan',
        'tweepy',
        'matplotlib',
        'numpy',
        'tabula-py',
        'infographics-nuuuwan',
        'pycountry-convert',
        'scipy',
        'emoji-country-flag',
        'google-api-python-client',
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
)
