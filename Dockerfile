
# build123d miniforge3 Dockerfile

#FROM quay.io/condaforge/miniforge3:25.3.0-1
FROM quay.io/condaforge/miniforge3:latest

RUN apt-get update && \
    export ENV TZ=US DEBIAN_FRONTEND=noninteractive && \
    apt-get install -y --no-install-recommends libgl1 libxrender1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN useradd -m -s /bin/bash vscode

COPY requirements.txt /requirements.txt
USER vscode
RUN pip3 install --user build123d ocp_vscode ipykernel -r /requirements.txt


WORKDIR /workspace