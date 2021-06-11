
import time
import setuptools

DIST_NAME = 'covid19'
with open("README.md", "r") as fh:
    long_description = fh.read()

IS_PRE_RELEASE = False
MAJOR, MINOR, PATCH = 1, 0, 0
if IS_PRE_RELEASE:
    ts = time.strftime('%Y%m%d_%H%M%S', time.localtime())
    version = '%d.%d.%d.%s' % (MAJOR, MINOR, PATCH, ts)
else:
    version = '%d.%d.%d' % (MAJOR, MINOR, PATCH)

setuptools.setup(
    name="%s-nuuuwan" % DIST_NAME,
    version=version,
    author="Nuwan I. Senaratna",
    author_email="nuuuwan@gmail.com",
    description="",
    long_description=long_description,
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

    install_requires=[],
    test_suite='nose.collector',
    tests_require=['nose'],
)
