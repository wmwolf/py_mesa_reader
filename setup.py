from setuptools import setup

setup(name='mesa_reader',
    version='0.3.0',
    description='tools for interacting with output from MESA star',
    author='William M. Wolf',
    author_email='wolfey6@gmail.com',
    license='MIT',
    packages=['mesa_reader'],
    install_requires=['numpy'],
    include_package_data=False,
    zip_safe=False)
