DOCKER_IMAGE_TAG ?= ""
ECR_URL ?= ""

deployimage:
	$(aws ecr get-login --no-include-email --region eu-west-2)\
	docker build -t epicgames . &&\
	docker tag ${DOCKER_IMAGE_TAG} ${ECR_URL}/${DOCKER_IMAGE_TAG} &&\
	docker push ${ECR_URL}/${DOCKER_IMAGE_TAG}
