from setuptools import setup, find_packages


setup(
    name='assignment0',
    version='1.0',
    author='Hydrogen',
    author_email='<NEED TO ADD>',
    url="<NEED TO ADD>",
    packages=find_packages(),
    install_requires=[
        'pypdf==4.0.0'
    ],
    tests_require=[
        'pytest==7.4.4',
        'pytest-mock==3.12.0',
    ]
)
