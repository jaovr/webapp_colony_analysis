import sys
import types

import numpy as np
import pytest


if "cv2" not in sys.modules:
    cv2_stub = types.SimpleNamespace()

    cv2_stub.HOUGH_GRADIENT = 0
    cv2_stub.COLOR_BGR2GRAY = 6

    def circle(image, center, radius, color, thickness):
        if thickness != -1:
            raise NotImplementedError("Stub only supports filled circles")
        cx, cy = center
        yy, xx = np.ogrid[: image.shape[0], : image.shape[1]]
        mask = (xx - cx) ** 2 + (yy - cy) ** 2 <= radius ** 2
        image[mask] = color
        return image

    def bitwise_and(src1, src2, mask=None):
        result = np.bitwise_and(src1, src2)
        if mask is None:
            return result
        mask_bool = mask.astype(bool)
        if mask_bool.ndim == 2 and result.ndim == 3:
            mask_bool = mask_bool[..., np.newaxis]
        return np.where(mask_bool, result, 0)

    cv2_stub.circle = circle
    cv2_stub.bitwise_and = bitwise_and
    cv2_stub.HoughCircles = None

    sys.modules["cv2"] = cv2_stub

import cv2

import app.pipeline as pipeline
from app.pipeline import (
    DEFAULT_DP,
    DEFAULT_MAX_RADIUS_FRACTION,
    DEFAULT_MIN_DIST_FRACTION,
    DEFAULT_MIN_RADIUS_FRACTION,
    DEFAULT_PARAM1,
    DEFAULT_PARAM2,
    run_pipeline,
)


def _expected_radius_bounds(
    min_dimension: int,
    min_fraction: float = DEFAULT_MIN_RADIUS_FRACTION,
    max_fraction: float = DEFAULT_MAX_RADIUS_FRACTION,
):
    min_radius = max(1.0, min_dimension * min_fraction)
    max_radius = max(min_radius + 1.0, min_dimension * max_fraction)

    min_radius_int = int(round(min_radius))
    max_radius_int = int(round(max_radius))
    if max_radius_int <= min_radius_int:
        max_radius_int = min_radius_int + 1

    return min_radius_int, max_radius_int


def _prepare_monkeypatched_io(monkeypatch, bgr_image: np.ndarray):
    gray_image = bgr_image.mean(axis=2).astype(np.uint8)
    monkeypatch.setattr(pipeline, "to_bgr", lambda _: bgr_image.copy())
    monkeypatch.setattr(pipeline, "to_gray", lambda _: gray_image.copy())
    monkeypatch.setattr(pipeline, "median_filter", lambda image, ksize=25: gray_image.copy())


def test_run_pipeline_applies_mask_across_multiple_sizes(monkeypatch):
    captured_calls = []

    def fake_hough(image, method, dp, minDist, param1, param2, minRadius, maxRadius):
        height, width = image.shape[:2]
        captured_calls.append(
            {
                "shape": (height, width),
                "dp": dp,
                "minDist": minDist,
                "param1": param1,
                "param2": param2,
                "minRadius": minRadius,
                "maxRadius": maxRadius,
            }
        )
        radius = max(1, min(height, width) // 4)
        center = (width // 2, height // 2, radius)
        return np.array([[center]], dtype=np.float32)

    monkeypatch.setattr(cv2, "HoughCircles", fake_hough)

    sizes = ((400, 400), (320, 500), (512, 256))
    for height, width in sizes:
        bgr_image = np.full((height, width, 3), 200, dtype=np.uint8)
        _prepare_monkeypatched_io(monkeypatch, bgr_image)

        result = run_pipeline(b"unused")

        assert result.shape == (height, width, 3)
        assert np.count_nonzero(result) < result.size

    assert len(captured_calls) == len(sizes)

    for call, (height, width) in zip(captured_calls, sizes):
        min_dimension = min(height, width)
        expected_min_dist = min_dimension * DEFAULT_MIN_DIST_FRACTION
        expected_min_radius, expected_max_radius = _expected_radius_bounds(min_dimension)

        assert call["shape"] == (height, width)
        assert call["dp"] == DEFAULT_DP
        assert call["param1"] == DEFAULT_PARAM1
        assert call["param2"] == DEFAULT_PARAM2
        assert call["minDist"] == pytest.approx(expected_min_dist)
        assert call["minRadius"] == expected_min_radius
        assert call["maxRadius"] == expected_max_radius


def test_run_pipeline_accepts_custom_circle_parameters(monkeypatch):
    captured_args = {}

    def fake_hough(image, method, dp, minDist, param1, param2, minRadius, maxRadius):
        captured_args.update(
            {
                "dp": dp,
                "minDist": minDist,
                "param1": param1,
                "param2": param2,
                "minRadius": minRadius,
                "maxRadius": maxRadius,
            }
        )
        height, width = image.shape[:2]
        radius = max(1, min(height, width) // 5)
        center = (width // 2, height // 2, radius)
        return np.array([[center]], dtype=np.float32)

    monkeypatch.setattr(cv2, "HoughCircles", fake_hough)

    custom_kwargs = {
        "dp": 1.5,
        "min_dist_fraction": 0.2,
        "min_radius_fraction": 0.1,
        "max_radius_fraction": 0.3,
        "param1": 180,
        "param2": 45,
    }

    bgr_image = np.full((300, 450, 3), 180, dtype=np.uint8)
    _prepare_monkeypatched_io(monkeypatch, bgr_image)

    run_pipeline(b"unused", **custom_kwargs)

    min_dimension = min(300, 450)
    expected_min_radius, expected_max_radius = _expected_radius_bounds(
        min_dimension,
        min_fraction=custom_kwargs["min_radius_fraction"],
        max_fraction=custom_kwargs["max_radius_fraction"],
    )

    assert captured_args["dp"] == custom_kwargs["dp"]
    assert captured_args["minDist"] == pytest.approx(min_dimension * custom_kwargs["min_dist_fraction"])
    assert captured_args["param1"] == custom_kwargs["param1"]
    assert captured_args["param2"] == custom_kwargs["param2"]
    assert captured_args["minRadius"] == expected_min_radius
    assert captured_args["maxRadius"] == expected_max_radius
