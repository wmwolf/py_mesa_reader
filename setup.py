from setuptools import setup

setup(
    name="mesa_reader",
    version="0.4.0",
    description="Tools for interacting with output from MESA star and MESA binary",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="http://github.com/wmwolf/py_mesa_reader",
    author="William M. Wolf",
    author_email="wolfwm@uwec.edu",
    license="LGPL-3.0-only",
    packages=["mesa_reader"],
    install_requires=["numpy", "pandas"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
