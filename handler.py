"""
RunPod serverless handler for Pixal3D — single image → 3D model generation.

Architecture:
  - Multi-view diffusion model + neural surface reconstruction
  - Texture baking with UV unwrapping
  - OBJ and GLB export support
  - ~12B parameters, ~4GB weights in fp16
  - Requires >=12GB VRAM

Environment (set by RunPod template):
  - RUNPOD_POD_ID       — auto
  - RUNPOD_AI_API_KEY   — auto

Input schema (via RunPod serverless job):
  {
    "input": {
      "image_base64": "<base64-encoded PNG/JPG>",  // REQUIRED — input image
      "detail_level": "medium",                     // optional — "low", "medium", "high"
      "output_format": "glb",                       // optional — "obj" or "glb"
      "texture_resolution": 1024                    // optional — 512, 1024, 2048
    }
  }

Output:
  {
    "model_obj_base64": "<base64 OBJ data>",
    "model_glb_base64": "<base64 GLB data>",
    "texture_base64": "<base64 texture map>",
    "wall_time_s": 45.2
  }
"""

import base64
import io
import os
import time
import traceback

# ── Environment setup ─────────────────────────────────────────────────────────
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

import torch

# Disable flash/mem-efficient SDPA for broader GPU compatibility
torch.backends.cuda.enable_flash_sdp(False)
torch.backends.cuda.enable_mem_efficient_sdp(False)
torch.backends.cuda.enable_math_sdp(True)

# ── Model path (baked into image at BUILD TIME) ──────────────────────────────
MODEL_ID = "/models/pixal3d"

# ── Global pipeline (loaded once, reused across jobs) ─────────────────────────
_pipe = None
_device = None


def load_pipeline():
    """Load Pixal3D pipeline once and cache globally."""
    global _pipe, _device
    if _pipe is not None:
        return _pipe, _device

    print("[Cold Start] Loading Pixal3D pipeline...", flush=True)
    t0 = time.time()

    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    print(f"  Device: {_device}, dtype: {dtype}", flush=True)

    # Import and load Pixal3D pipeline
    # This is a placeholder — actual import path depends on model packaging
    # For now we use the generic pipeline loading pattern
    from pixal3d import Pixal3DPipeline

    pipe = Pixal3DPipeline.from_pretrained(
        MODEL_ID,
        torch_dtype=dtype,
    )

    # Move fully to GPU
    pipe = pipe.to(_device)

    print(f"[Cold Start] Pipeline ready in {time.time() - t0:.1f}s", flush=True)

    _pipe = pipe
    return _pipe, _device


def process_image(image_base64: str) -> bytes:
    """Decode base64 image to bytes."""
    return base64.b64decode(image_base64)


def model_to_base64(file_path: str) -> str:
    """Read a model file and return base64-encoded string."""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def run_inference(
    image_bytes: bytes,
    detail_level: str = "medium",
    output_format: str = "glb",
    texture_resolution: int = 1024,
) -> tuple:
    """
    Run Pixal3D inference.

    Returns (obj_base64, glb_base64, texture_base64, wall_time_s).
    """
    pipe, device = load_pipeline()

    print(f"[Inference] Generating 3D model from input image", flush=True)
    print(
        f"  detail={detail_level}, format={output_format}, "
        f"texture_res={texture_resolution}",
        flush=True,
    )

    t_start = time.time()

    # Run inference
    with torch.inference_mode():
        with torch.cuda.amp.autocast(enabled=True):
            result = pipe(
                image=image_bytes,
                detail_level=detail_level,
                output_format=output_format,
                texture_resolution=texture_resolution,
            )

    wall_time = time.time() - t_start
    print(f"[Done] Generation took {wall_time:.1f}s", flush=True)

    # result contains paths or bytes for obj, glb, texture
    obj_b64 = result.get("obj_base64", "")
    glb_b64 = result.get("glb_base64", "")
    texture_b64 = result.get("texture_base64", "")

    return obj_b64, glb_b64, texture_b64, wall_time


# ═══════════════════════════════════════════════════════════════════════════════
# RunPod Serverless Handler
# ═══════════════════════════════════════════════════════════════════════════════


def handler(job):
    """
    RunPod serverless handler: image → 3D model.

    Called once per job. The pipeline stays loaded across jobs (global).
    """
    job_input = job.get("input", {})
    image_base64 = job_input.get("image_base64", "")

    if not image_base64:
        return {"error": "Missing required field: image_base64"}

    detail_level = str(job_input.get("detail_level", "medium")).lower()
    output_format = str(job_input.get("output_format", "glb")).lower()
    texture_resolution = int(job_input.get("texture_resolution", 1024))

    # Validate parameters
    valid_detail = {"low", "medium", "high"}
    if detail_level not in valid_detail:
        return {"error": f"Invalid detail_level: {detail_level}. Must be one of {valid_detail}"}

    valid_formats = {"obj", "glb"}
    if output_format not in valid_formats:
        return {"error": f"Invalid output_format: {output_format}. Must be one of {valid_formats}"}

    valid_texture_res = {512, 1024, 2048}
    if texture_resolution not in valid_texture_res:
        return {"error": f"Invalid texture_resolution: {texture_resolution}. Must be one of {valid_texture_res}"}

    try:
        # Decode input image
        print("[Worker] Decoding input image...", flush=True)
        image_bytes = process_image(image_base64)

        # Run inference
        obj_b64, glb_b64, texture_b64, wall_time = run_inference(
            image_bytes=image_bytes,
            detail_level=detail_level,
            output_format=output_format,
            texture_resolution=texture_resolution,
        )

        result = {
            "wall_time_s": round(wall_time, 1),
        }

        if obj_b64:
            result["model_obj_base64"] = obj_b64
        if glb_b64:
            result["model_glb_base64"] = glb_b64
        if texture_b64:
            result["texture_base64"] = texture_b64

        return result

    except Exception as exc:
        traceback.print_exc()
        return {
            "error": f"Pixal3D inference failed: {str(exc)}",
            "traceback": traceback.format_exc(),
        }


# ── Entrypoint ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import runpod

    runpod.serverless.start({"handler": handler})
