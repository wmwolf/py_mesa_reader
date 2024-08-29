from setuptools import setup

setup(name='mesa_reader',
    version='0.3.4',
    description='Tools for interacting with output from MESA star and MESA binary',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='http://github.com/wmwolf/py_mesa_reader',
    author='William M. Wolf',
    author_email='wolfwm@uwec.edu',
    license='MIT',
    packages=['mesa_reader'],
    install_requires=['numpy'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.6'
    )
