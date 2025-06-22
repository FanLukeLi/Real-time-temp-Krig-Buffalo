FROM continuumio/miniconda3
COPY environment.yml .
RUN conda env create -f environment.yml
RUN apt-get update && apt-get install -y openjdk-17-jdk
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH
SHELL ["conda", "run", "-n", "base", "/bin/bash", "-c"]
