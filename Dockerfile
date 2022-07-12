FROM kbase/sdkbase2:python
MAINTAINER KBase Developer
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

RUN apt-get update

# Install gcc, a dependency for the python packages below
RUN apt-get install -y gcc

# Install pip in order to install python packages
RUN python -m pip install --upgrade pip

# Dependencies of Source Tracker are:
# numpy pandas scipy scikit-bio biom-format h5py seaborn

# Install Source Tracker

# with conda, not working
#FROM continuumio/miniconda3:4.6.14
#RUN conda update -n base -c defaults conda
#RUN conda create -n st2 -c biocore python=3.5 numpy scipy scikit-bio biom-format h5py seaborn
#RUN pip install sourcetracker

# from GitHub
RUN pip install https://github.com/biota/sourcetracker2/archive/master.zip

# Test that Source Tracker was installed
RUN sourcetracker2 gibbs --help

# -----------------------------------------

COPY ./ /kb/module

RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
