FROM ghcr.io/andrewembry312-hub/elabs-server/pixal3d-runpod:latest
LABEL maintainer="E-Labs AI Studio" description="Pixal3D — Image to 3D model on RunPod"
ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
COPY handler.py /workspace/handler.py
WORKDIR /workspace
CMD ["python", "-u", "handler.py"]
