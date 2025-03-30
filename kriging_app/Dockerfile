FROM continuumio/anaconda3:latest

WORKDIR /kriging_app

COPY kriging_app /kriging_app/

COPY environment.yml .

RUN conda env create -f environment.yml && \
    echo "source activate kriging_app" > ~/.bashrc

RUN source activate kriging_app && \
    conda install gunicorn

RUN source activate kriging_app && \
    python prepare_grid.py

EXPOSE 8086

CMD ["conda", "run", "-n", "kriging_app", "gunicorn", "--bind", "0.0.0.0:8086", "--workers=4", "app_name:app"]
