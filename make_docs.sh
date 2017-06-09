#! /usr/bin/env bash

# this calls sphinx to make the docs into docs_build from docs_source (see
# Makefile) and then moves the html product into the docs directory

make html
mv docs_build/html docs
