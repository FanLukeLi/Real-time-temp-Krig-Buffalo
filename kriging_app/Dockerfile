FROM continuumio/miniconda3:latest

WORKDIR /kriging_app

COPY . /kriging_app/

RUN conda env create -f environment.yml

RUN conda run -n kriging_app_env python ./realtime_krig/make_initial_map.py

RUN chmod 777 ./result/raster_map.html

USER root

EXPOSE 8086

CMD ["conda", "run", "-n", "kriging_app_env", "gunicorn", "--bind", "0.0.0.0:8086", "--workers=1", "app:app"]
