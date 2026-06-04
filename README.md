# elabs / Pixal3D

[![Deploy on RunPod](https://img.shields.io/badge/RunPod-Deploy-orange?logo=runpod)](https://console.runpod.io/hub)
[![CUDA 12.4](https://img.shields.io/badge/CUDA-12.4-green)](https://developer.nvidia.com/cuda-toolkit)

Generate high-quality **3D models from a single input image**. Supports OBJ and GLB export, texture baking, and multiple detail levels. Built on multi-view diffusion + neural surface reconstruction.

![Pixal3D](https://pub-796a08821c1c483aaf5e274e0d03e350.r2.dev/hub-icons/pixal3d.svg)

## Highlights

- Single image to 3D -- no multi-view setup required
- OBJ + GLB export -- ready for Blender, Unity, Three.js
- Texture baking -- UV-unwrapped texture maps included
- Detail levels -- low/medium/high polygon counts
- Fully serverless -- no network volume required

## Quick Start

```bash
curl -X POST https://api.runpod.ai/v2/{ENDPOINT_ID}/run \
  -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"image_base64": "<base64 PNG>", "output_format": "glb", "detail_level": "medium"}}'
```

## API

### Input

```json
{
  "input": {
    "image_base64": "<base64 PNG or JPG>",
    "detail_level": "medium",
    "output_format": "glb",
    "texture_resolution": 1024
  }
}
```

### Output

```json
{
  "model_glb_base64": "<base64 GLB file>",
  "model_obj_base64": "<base64 OBJ file>",
  "texture_base64": "<base64 PNG texture>",
  "detail_level": "medium",
  "wall_time_s": 45.0
}
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `image_base64` | string | required | Base64 PNG/JPG input image |
| `detail_level` | string | `"medium"` | Mesh density: "low", "medium", "high" |
| `output_format` | string | `"glb"` | Export: "glb", "obj", "both" |
| `texture_resolution` | int | `1024` | Texture resolution: 512, 1024, 2048 |

## Best Input Images

- Subject isolated on clean/white background
- Front-facing view
- Good lighting, no heavy shadows
- 512x512 to 2048x2048 pixels
- PNG or JPG format

## GPU Requirements

- Minimum: >=12GB VRAM
- Recommended: RTX 4090, L40S, A6000 (>=24GB VRAM)
- CUDA: 12.4+

## License

Based on Pixal3D architecture. Check model weights license for commercial terms.
