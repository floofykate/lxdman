import setuptools

with open("README.md") as readme_file:
    long_description = readme_file.read()

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.readlines()

setuptools.setup(
    name="lxdman",
    version="0.0.1",
    author="floofykate",
    author_email="kat@floofy.club",
    description="LXD Tooling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/floofykate/lxdman",
    packages=setuptools.find_packages(),
    package_dir={'lxdman': 'lxdman'},
    entry_points={
        'console_scripts': [
            'lxdman = lxdman.app:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    install_requires=requirements,
    zip_safe=False,
    python_requires='>=3.8'
)
