# elabs / Pixal3D — Image to 3D Model Generation

[![Run on RunPod](https://runpod.io/badge/runpod-hub)](https://runpod.io/console/hub)

Generate high-quality **3D models** from a single input image using Pixal3D. Outputs OBJ, GLB, with baked textures. Powered by advanced multi-view diffusion and neural surface reconstruction. Runs on RunPod serverless — no network volume required.

## Highlights

- **Single image → full 3D model** with texture baking
- **OBJ and GLB export** formats supported
- **Multiple detail levels**: low (fast), medium, high (quality)
- **Configurable texture resolution**: 512, 1024, 2048
- **Weights baked into image** — no cold-download delays
- **12GB+ VRAM required** for high-detail mode
- **Apache-2.0** licensed

## API

### Input

```json
{
  "input": {
    "image_base64": "<base64-encoded PNG/JPG image>",
    "detail_level": "medium",
    "output_format": "glb",
    "texture_resolution": 1024
  }
}
```

### Output

```json
{
  "model_obj_base64": "<base64 OBJ data>",
  "model_glb_base64": "<base64 GLB data>",
  "texture_base64": "<base64 texture map>",
  "wall_time_s": 45.2
}
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `image_base64` | string | **required** | Base64-encoded input image (PNG or JPG) |
| `detail_level` | string | `"medium"` | Detail level: `"low"`, `"medium"`, or `"high"` |
| `output_format` | string | `"glb"` | Output format: `"obj"` or `"glb"` |
| `texture_resolution` | int | `1024` | Texture resolution in pixels: `512`, `1024`, or `2048` |

## GPU Requirements

| Detail Level | Min VRAM | Recommended GPUs |
|---|---|---|
| Low | 12 GB | RTX 4090, A5000 24GB |
| Medium | 16 GB | RTX 4090, L40S, A6000 |
| High | 24 GB | L40S, A6000, RTX 6000 Ada |

- **CUDA**: 12.0+

## Benchmark

| GPU | Detail Level | Texture Res | Time |
|---|---|---|---|
| RTX 4090 | Low | 1024 | ~30s |
| RTX 4090 | Medium | 1024 | ~60s |
| RTX 4090 | High | 2048 | ~150s |
| L40S | High | 2048 | ~90s |
| A6000 | High | 2048 | ~100s |

## License

Apache-2.0
