FROM continuumio/anaconda3:latest

WORKDIR /kriging_app

COPY kriging_app, /kriging_app/

RUN conda env create -f environment.yml

RUN conda run -n kriging_app

EXPOSE 8086

