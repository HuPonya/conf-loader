# python docker base image with conf-loader
#
# VERSION               0.0.1
# PYTHON_VERSION        2.7.12

FROM registry.9fwealth.com:5000/base/python:2.7.12
MAINTAINER i@hupo.me

COPY . /app/conf-loader

RUN pip install -r /app/conf-loader/requirements-python-2.txt
