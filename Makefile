
# workboard Makefile

default: help

help:
	@echo "help	 	-- print help"
	@echo "run           -- python ./workboard/workboard01.py"
	@echo "podman-build  -- podman build . -t "
	@echo "podman-run	 -- podman run --name \$$PODMAN_INSTANCE_NAME \$$PODMAN_IMAGE_NAME"
	@echo "podman-exec   -- podman exec --name \$$PODMAN_INSTANCE_NAME"
	@echo "svg2build123d -- build123d..import_svg_as_buildline_code($SVG_PATH)''
	cat ./Makefile | grep -E '^\w|'$$'\t'


PYTHON=python
#PYTHON=/opt/conda/bin/python
run:
	$(PYTHON) workboard/workboard01.py


PODMAN_IMAGE_TAG=0.0.1
#PODMAN_IMAGE_TAG="latest"
PODMAN_IMAGE_NAME=westurner/workboard:${PODMAN_IMAGE_TAG}

podman-build:
	podman build . -t "${PODMAN_IMAGE_NAME}"


PODMAN_RM=
#PODMAN_RM=--rm

PODMAN_INSTANCE_NAME ?=workboard0

podman-run:
	podman run ${PODMAN_RM} -it --name "${PODMAN_INSTANCE_NAME}" "${PODMAN_IMAGE_NAME}"

podman-exec-bash:
	podman exec -it "${PODMAN_INSTANCE_NAME}" bash --login

check:
	ls -al .devcontainer/{devcontainer.json,podman-rootless} Dockerfile environment.yml requirements.txt
	test -f .devcontainer/podman-rootless
	test -x .devcontainer/podman-rootless
	@echo "# Check whether podman-rootless is on \$$PATH:"
	@echo "PATH=${PATH}"
	test -p "podman-rootless"



import_svg_as_buildline_code=python -c "import build123d,sys; print(build123d.importers.import_svg_as_buildline_code(sys.argv[1])[0])"
svg2build123d:
	test -n "${SVG_PATH}"
	$(import_svg_as_buildline_code) ${SVG_PATH}

WORKBOARD_SVG_FILE=./workboard/workboard01__groove_handle_2d_v0.0.4.svg
svg2build123d-workboard01:
	$(MAKE) svg2build123d SVG_PATH=${WORKBOARD_SVG_FILE}


pytest:
	pytest -v ./workboard

pytestx:
	pytest -x -v ./workboard