
# Dockerfile for CAD with build123d, ocp_vscode, ipykernel, pip, mamba

#Dockerfile: https://github.com/conda-forge/miniforge-images/blob/master/ubuntu/Dockerfile
#FROM docker.io/condaforge/miniforge3:latest
#FROM quay.io/condaforge/miniforge3:25.3.0-1
FROM quay.io/condaforge/miniforge3:latest

LABEL org.opencontainers.image.description="A devcontainer for CAD with build123d, ocp_vscode, ipykernel, pip, and mamba"
LABEL org.opencontainers.image.source=https://github.com/westurner/workboard/tree/main/Dockerfile
LABEL org.opencontainers.image.url=https://github.com/westurner/workboard
LABEL org.opencontainers.image.authors=@westurner

RUN --mount=type=cache,id=aptcache0,target=/var/cache/apt,sharing=shared \
    apt-get update && \
    export ENV TZ=US DEBIAN_FRONTEND=noninteractive && \
    apt-get install -y --no-install-recommends sudo libgl1 libxrender1 \
        \
        make less bash-completion openssh-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV NB_USER=vscode
ENV NB_UID=1000
RUN --mount=type=cache,id=aptcache0,target=/var/cache/apt,sharing=shared \
    userdel -r ubuntu && \
    useradd -m -s /bin/bash --uid "${NB_UID}" -G sudo "${NB_USER}" && \
    export HOME="/home/${NB_USER}" && \
    (sudo -u "${NB_USER}" \
        echo 'export PATH="${PATH}:${HOME}/.local/bin"') >> "${HOME}/.bashrc"


COPY requirements.txt /requirements.txt
RUN --mount=type=cache,id=pipcache0,target=/home/${NB_USER}/.cache/pip,uid=${NB_UID},sharing=shared \
    --mount=type=cache,id=uvcache0,target=/home/${NB_USER}/.cache/uv,uid=${NB_UID},sharing=shared \
    chown -R ${NB_USER} /home/${NB_USER}/.cache

USER ${NB_USER}
ENV REQUIREMENTS_TXT=/requirements.txt
RUN --mount=type=cache,id=pipcache0,target=/home/${NB_USER}/.cache/pip,uid=${NB_UID},sharing=shared \
    --mount=type=cache,id=uvcache0,target=/home/${NB_USER}/.cache/uv,uid=${NB_UID},sharing=shared \
    which python3 && \
    python3 -m site
    # python3 -m pip install uv && \
    # ~/.local/bin/uv pip install --system build123d ocp_vscode ipykernel \
    #     ${REQUIREMENTS_TXT:+"-r"} \
    #     ${REQUIREMENTS_TXT:+"${REQUIREMENTS_TXT}"}

ENV ENVIRONMENT_YML=/environment.yml
COPY ${ENVIRONMENT_YML} /environment.yml

USER root
RUN --mount=type=cache,id=condacache0,target=/opt/conda/pkgs,uid=${NB_UID},sharing=shared \
    mamba install -y -f "${ENVIRONMENT_YML?ERROR: must be specified}"

USER ${NB_USER}
WORKDIR /workspaces