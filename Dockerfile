FROM ubuntu:20.04
MAINTAINER Michele Dallachiesa <michele.dallachiesa@sigforge.com>

USER root
ENV DEBIAN_FRONTEND=noninteractive

# Update package list, upgrade system and set default locale
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install apt-utils
RUN apt-get -y install locales
RUN locale-gen "en_US.UTF-8"
ENV LC_ALL "en_US.UTF-8"
ENV LANG "en_US.UTF-8"

# Install python3, and activate python3.8 as default python interpreter
RUN apt-get -y install python3-dev python3 python3-pip python3-venv
RUN pip3 install --upgrade pip
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1

# install additional packages
RUN apt-get -y install ssh htop git vim net-tools

# Install python packages for data science
ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# add Jupyter config
ADD jupyter_notebook_config.py /root/.jupyter/jupyter_notebook_config.py

# Build/activate ipywidgets extension
RUN apt-get -y install npm build-essential nodejs
RUN jupyter nbextension enable --py widgetsnbextension
# Depending on the Jupyterlab version, there's a different command to run:
# https://github.com/jupyter-widgets/ipywidgets/tree/master/packages/jupyterlab-manager
RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager@2.0

# Install additional Jupyterlab extensions
RUN jupyter labextension install @jupyterlab/toc

RUN apt-get -y install texlive
RUN apt-get -y install pandoc texlive-xetex

# add /shared to pythonpath: packages defined in this directory will be visible from Python.
ENV PYTHONPATH /shared

WORKDIR /shared

CMD ["jupyter", "lab"]

EXPOSE 8888/tcp

