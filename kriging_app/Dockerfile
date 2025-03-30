FROM continuumio/miniconda3:latest

WORKDIR /kriging_app

COPY . /kriging_app/

RUN conda env create -f environment.yml

RUN conda run -n kriging_app ./realtime_krig/make_initial_map.py

RUN chmod 777 ./resulst/raster_map.html

EXPOSE 8086

CMD ["conda", "run", "-n", "kriging_app", "gunicorn", "--bind", "0.0.0.0:8086", "--workers=1", "app:app"]
