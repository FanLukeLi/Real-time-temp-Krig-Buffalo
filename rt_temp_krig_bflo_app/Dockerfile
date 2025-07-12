FROM continuumio/miniconda3

COPY environment.yml .

RUN conda env create -f environment.yml
RUN apt-get update && apt-get install -y openjdk-17-jdk
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

#COPY /opt/spark/python /opt/spark/python/
#COPY /opt/spark/python/lib/py4j-0.10.9.9-src.zip /opt/spark/python/lib/
#ENV PYTHONPATH=/opt/spark/python:/opt/spark/python/lib/py4j-0.10.9.9-src.zip

SHELL ["conda", "run", "-n", "base", "/bin/bash", "-c"]

