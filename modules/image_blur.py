"""Detects faces in an image and blurs them, entirely on the local machine."""

import cv2
import numpy as np
from PIL import Image

# OpenCV ships this pretrained model file; no download or API key needed.
_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
_face_cascade = cv2.CascadeClassifier(_CASCADE_PATH)


def _pil_to_cv2(pil_image):
    """Convert a PIL image (RGB) to an OpenCV image (BGR)."""
    rgb_array = np.array(pil_image.convert("RGB"))
    return cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)


def _cv2_to_pil(cv2_image):
    """Convert an OpenCV image (BGR) back to a PIL image (RGB)."""
    rgb_array = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb_array)


def detect_and_blur_faces(pil_image, blur_strength=51):
    """Find faces in pil_image and return (blurred_image, face_count).

    blur_strength must be odd (OpenCV's Gaussian blur requirement); it is
    rounded up to the nearest odd number automatically.
    """
    if blur_strength % 2 == 0:
        blur_strength += 1

    cv_image = _pil_to_cv2(pil_image)
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

    faces = _face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
    )

    for (x, y, w, h) in faces:
        region = cv_image[y:y + h, x:x + w]
        blurred_region = cv2.GaussianBlur(region, (blur_strength, blur_strength), 0)
        cv_image[y:y + h, x:x + w] = blurred_region

    return _cv2_to_pil(cv_image), len(faces)
