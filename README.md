# elabs / Pixal3D

Image-to-3D generation. Upload a single image and get back a 3D mesh (GLB) with preview render.

[![Docker Build](https://github.com/ELABS-AI/pixal3d-runpod-worker/actions/workflows/build.yml/badge.svg)](https://github.com/ELABS-AI/pixal3d-runpod-worker/actions/workflows/build.yml)

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `HF_HOME` | `/runpod-volume/models/huggingface` | HuggingFace cache directory |
| `HUGGINGFACE_HUB_CACHE` | `/runpod-volume/models/huggingface/hub` | HuggingFace hub cache |

## Input

```json
{"input": {"image_b64": "<base64 PNG/JPG>"}}
```

## Output

```json
{"mesh_b64": "<base64 GLB>", "preview_b64": "<base64 PNG>", "wall_time_s": 15.0}
```

## GPU Requirements

RTX 3090+ (24GB VRAM) | ~10-20s per mesh | Apache 2.0 license

## Built by [E-Labs AI](https://www.elabsai.com)
