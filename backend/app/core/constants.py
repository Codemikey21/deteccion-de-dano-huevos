"""Constantes del dominio de detección."""

CLASS_ID_EGG = 0
CLASS_ID_CRACK = 1

CLASS_NAMES: dict[int, str] = {
    CLASS_ID_EGG: "egg",
    CLASS_ID_CRACK: "crack",
}

MODEL_NAME = "yolov8n"
MODEL_IMGSZ = 960

SERVICE_NAME = "egg-detection-api"
API_TITLE = "Egg Detection API"
API_VERSION = "0.1.0"

STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"
STATUS_UNKNOWN = "unknown"

ROUTE_ACCEPT = "accept"
ROUTE_REJECT = "reject"
ROUTE_REVIEW = "review"

REASON_NO_CRACK = "no_crack_detected"
REASON_CRACK = "crack_detected"
REASON_NO_EGG = "egg_not_detected"

ALLOWED_IMAGE_MEDIA_TYPES = frozenset({"image/jpeg", "image/png", "image/jpg"})
