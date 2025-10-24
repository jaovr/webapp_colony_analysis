from pathlib import Path

import numpy as np
import pytest

cv2 = pytest.importorskip("cv2", reason="requires OpenCV", exc_type=ImportError)

from app.pipeline import run_pipeline


def test_run_pipeline_returns_normalized_rgb_and_gray_images():
    img_path = Path(__file__).parent / "13895.jpg"
    file_bytes = img_path.read_bytes()

    result = run_pipeline(file_bytes)

    assert set(result.keys()) == {"rgb", "gray"}

    rgb = result["rgb"]
    assert rgb.shape == (224, 224, 3)
    assert rgb.dtype == np.float32
    assert np.all(rgb >= 0.0)
    assert np.all(rgb <= 1.0)

    gray = result["gray"]
    assert gray.shape == (224, 224)
    assert gray.dtype == np.float32
    assert np.all(gray >= 0.0)
    assert np.all(gray <= 1.0)


def test_run_pipeline_respects_custom_output_size():
    img_path = Path(__file__).parent / "13895.jpg"
    file_bytes = img_path.read_bytes()

    result = run_pipeline(file_bytes, output_size=(128, 128))

    rgb = result["rgb"]
    assert rgb.shape == (128, 128, 3)

    gray = result["gray"]
    assert gray.shape == (128, 128)
