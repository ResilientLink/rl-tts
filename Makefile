.PHONY: help build push deploy test clean

help:
	@echo "RL-TTS Service Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  build    - Build Docker image"
	@echo "  push     - Push Docker image to registry"
	@echo "  deploy   - Deploy to Kubernetes"
	@echo "  test     - Run service tests"
	@echo "  clean    - Clean build artifacts"
	@echo ""

build:
	docker build -t yeager1977/rl-tts:latest .

push: build
	docker push yeager1977/rl-tts:latest

deploy: push
	kubectl apply -f k8s/rl-tts.yaml
	@echo "Waiting for deployment..."
	kubectl rollout status deployment/rl-tts -n rl-edge

test:
	python test_client.py --health
	python test_client.py --text "Hello, this is a test" --language en

clean:
	rm -f build.log
	rm -f test_output.raw
	docker rmi yeager1977/rl-tts:latest 2>/dev/null || true

