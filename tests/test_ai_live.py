"""Live integration test — generates 3 images with 3 providers.

Run manually with:
    uv run pytest tests/test_ai_live.py -v -s

Requires API keys in .env (STX_OPENAI_API_KEY, STX_GOOGLE_AI_KEY, STX_FAL_KEY).
"""

import os
import shutil
from pathlib import Path

import pytest
from dotenv import load_dotenv

from streamtex.ai.config import AIImageConfig
from streamtex.ai.generate import generate_image

# Load .env from the library root (must happen before tests check env vars)
load_dotenv(Path(__file__).parent.parent / ".env")

# Output directory in the AI manual
_AI_MANUAL_IMAGES = str(
    Path(__file__).parent.parent.parent
    / "streamtex-docs" / "manuals" / "stx_manual_ai" / "static" / "images" / "ai"
)

# Descriptive filenames for the manual
_TESTS = [
    {
        "provider": "openai",
        "prompt": (
            "A minimalist flat-design illustration of an AI brain connected "
            "to image generation, dark background, blue and violet gradient "
            "nodes, clean vector style, no text"
        ),
        "filename": "ai_openai_demo.png",
        "env_key": "STX_OPENAI_API_KEY",
    },
    {
        "provider": "google",
        "prompt": (
            "A photorealistic futuristic workspace with holographic screens "
            "showing AI-generated artwork, soft ambient lighting, "
            "cinematic composition, no text"
        ),
        "filename": "ai_google_demo.png",
        "env_key": "STX_GOOGLE_AI_KEY",
    },
    {
        "provider": "fal",
        "prompt": (
            "A beautiful abstract digital art composition with flowing "
            "gradients of blue, violet and cyan, geometric shapes, "
            "dark background, modern design, no text"
        ),
        "filename": "ai_fal_demo.png",
        "env_key": "STX_FAL_KEY",
    },
]


@pytest.mark.live
@pytest.mark.parametrize("test_case", _TESTS, ids=lambda t: t["provider"])
def test_generate_image_live(test_case, tmp_path):
    """Generate an image with each provider and copy to AI manual static/."""
    env_key = test_case["env_key"]
    if not os.environ.get(env_key):
        pytest.skip(f"{env_key} not set")

    cfg = AIImageConfig(
        provider=test_case["provider"],
        output_dir=str(tmp_path),
        auto_generate=True,
    )

    # Generate
    result_path = generate_image(
        test_case["prompt"],
        provider=test_case["provider"],
        size="1024x1024",
        config=cfg,
    )

    # Verify the file was created
    assert os.path.isfile(result_path), f"Image not created: {result_path}"
    file_size = os.path.getsize(result_path)
    assert file_size > 1000, f"Image too small ({file_size} bytes), likely corrupted"

    print(f"\n  [{test_case['provider']}] Generated: {result_path} ({file_size:,} bytes)")

    # Copy to AI manual static directory with a descriptive name
    os.makedirs(_AI_MANUAL_IMAGES, exist_ok=True)
    dest = os.path.join(_AI_MANUAL_IMAGES, test_case["filename"])
    shutil.copy2(result_path, dest)
    print(f"  [{test_case['provider']}] Copied to: {dest}")
