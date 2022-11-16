# python3 setup.py build_ext -i

from setuptools import setup, Extension

setup(
    name='krb5',
    version='0.0.1',
    author='vladimir Savchenko',
    author_email='voldmir@mail.ru',
    description='krb5 protocol',
    ext_modules=[Extension(
        'krb5',
        ['krb5.c'],
        libraries=['krb5']
)]

)
