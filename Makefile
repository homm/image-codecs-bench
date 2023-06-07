.PHONY: build shell run

TAG ?= latest

.docker_build: Dockerfile
	docker build . -t image-codecs-bench:${TAG} --iidfile .docker_build

build: .docker_build

shell: build
	docker run -it --rm -v ${PWD}:/opt image-codecs-bench:${TAG} sh
