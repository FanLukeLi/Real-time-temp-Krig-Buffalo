FROM continuumio/anaconda3:latest

WORKDIR /kriging_app

COPY . /kriging_app/

COPY environment.yml .

RUN conda env create -f environment.yml

RUN conda run -n kriging_app python make_initial_map.py

EXPOSE 8086

CMD ["conda", "run", "-n", "kriging_app", "gunicorn", "--bind", "0.0.0.0:8086", "--workers=4", "app:app"]
