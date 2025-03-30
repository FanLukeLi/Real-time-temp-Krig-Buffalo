FROM continuumio/anaconda3:latest

WORKDIR /kriging_app

COPY kriging_app, /kriging_app/

RUN conda env create -f environment.yml

RUN conda run -n kriging_app

RUN conda install gunicorn

RUN python prepare_grid.py

EXPOSE 8086

