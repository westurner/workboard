
# workboard Makefile

default: help

help:
	@echo "help	 	-- print help"
	@echo "podman-build  -- podman build . -t "
	@echo "podman-run	 -- podman run --name \$$PODMAN_INSTANCE_NAME \$$PODMAN_IMAGE_NAME"
	@echo ""
	cat ./Makefile | grep -E '^\w|'$$'\t'

PODMAN_IMAGE_TAG="0.0.1"
#PODMAN_IMAGE_TAG="latest"
PODMAN_IMAGE_NAME="westurner/workboard:${PODMAN_IMAGE_TAG}"

podman-build:
	podman build . -t "${PODMAN_IMAGE_NAME}"


PODMAN_RM=
#PODMAN_RM=--rm

PODMAN_INSTANCE_NAME="workboard0"

podman-run:
	podman run ${PODMAN_RM} -it --name "${PODMAN_INSTANCE_NAME}" "${PODMAN_IMAGE_NAME}"

check:
	ls -al .devcontainer/{devcontainer.json,podman-rootless} Dockerfile environment.yml requirements.txt
	test -f .devcontainer/podman-rootless
	test -x .devcontainer/podman-rootless
	@echo "# Check whether podman-rootless is on \$$PATH:"
	@echo "PATH=${PATH}"
	test -p "podman-rootless"


PYTHON=python
#PYTHON=/opt/conda/bin/python
run:
	$(PYTHON) workboard/workboard01.py

