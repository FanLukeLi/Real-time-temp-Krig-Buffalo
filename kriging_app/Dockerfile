FROM continuumio/anaconda3:latest

WORKDIR /kriging_app_v1

COPY data, kriging_app, result, /kriging_app_v1/

RUN conda env create -f environment.yml