FROM continuumio/miniconda3:latest

WORKDIR /kriging_app

COPY . /kriging_app/

RUN conda env create -n environment.yml

RUN conda run -n kriging_app_env python /kriging_app/realtime_krig/make_initial_map.py

RUN chmod 777 /kriging_app/result/raster_map.html

USER root

EXPOSE 8086

CMD ["conda", "run", "-n", "kriging_app", "gunicorn", "--bind", "0.0.0.0:8086", "--workers=1", "--access-logfile", "/var/log/gunicorn/access.log", "--error-logfile", "/var/log/gunicorn/error.log", "app:app"]
