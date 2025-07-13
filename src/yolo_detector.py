# src/yolo_detector.py

import os
import json
import logging
from ultralytics import YOLO
from datetime import datetime

# --- 1. Configuration and Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("yolo_detection.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Paths (relative to the /app directory inside Docker)
# Since yolo_detector.py is now in /app/src, go up one level (..) to /app, then down into data/raw/...
MEDIA_INPUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../data/raw/telegram_media"
)
METADATA_INPUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../data/raw/telegram_messages"
)
YOLO_OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../data/raw/yolo_detections"
)

os.makedirs(YOLO_OUTPUT_DIR, exist_ok=True)

# --- 2. Load YOLOv8 Model ---
# ... (rest of the script is the same) ...

# --- 2. Load YOLOv8 Model ---
# Load a pretrained YOLOv8n model (n for nano, a smaller, faster model)
# You can choose 'yolov8s.pt' (small), 'yolov8m.pt' (medium), 'yolov8l.pt' (large) for better accuracy but slower.
# The model will be downloaded automatically the first time.
model = YOLO("yolov8n.pt")
logger.info("YOLOv8n model loaded successfully.")


# --- 3. Object Detection Function ---
def detect_objects_in_image(image_path):
    """
    Runs YOLOv8 detection on a single image and returns formatted results.
    """
    detections = []
    try:
        # Predict objects in the image
        # conf=0.25 (confidence threshold), iou=0.7 (IoU threshold for NMS)
        results = model.predict(source=image_path, conf=0.25, iou=0.7, verbose=False)

        for result in results:
            # Iterate through detected boxes
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = model.names[class_id]  # Get class name from model

                detections.append(
                    {
                        "detected_object_class": class_name,
                        "confidence_score": confidence,
                    }
                )
    except Exception as e:
        logger.error(f"Error processing image {image_path}: {e}")
    return detections


# --- 4. Main Detection Loop ---
def run_detection_pipeline():
    logger.info("Starting YOLO object detection pipeline.")
    all_detection_results = []
    processed_image_paths = (
        set()
    )  # To avoid processing the same image twice if linked by multiple metadata entries

    # Iterate through the JSON metadata files to get message_id and local_media_path
    today_str = datetime.now().strftime("%Y-%m-%d")
    metadata_channel_dir = os.path.join(METADATA_INPUT_DIR, today_str)

    if not os.path.exists(metadata_channel_dir):
        logger.warning(
            f"No metadata found for today in {metadata_channel_dir}. Skipping detection."
        )
        return

    for json_file in os.listdir(metadata_channel_dir):
        if json_file.endswith(".json"):
            json_path = os.path.join(metadata_channel_dir, json_file)
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    messages = json.load(f)

                for message in messages:
                    message_id = message.get("message_id")
                    local_media_path_relative = message.get("local_media_path")

                    if message_id and local_media_path_relative:
                        # Construct the absolute path inside the container's file system
                        # local_media_path from scrape.py is already an absolute path relative to the container mount
                        image_full_path = local_media_path_relative

                        # Check if the path actually exists and is an image, and if not already processed
                        if (
                            os.path.exists(image_full_path)
                            and image_full_path.lower().endswith(
                                (".png", ".jpg", ".jpeg")
                            )
                            and image_full_path not in processed_image_paths
                        ):
                            logger.info(
                                f"Detecting objects in image for message {message_id}: {image_full_path}"
                            )
                            detections = detect_objects_in_image(image_full_path)

                            for det in detections:
                                all_detection_results.append(
                                    {
                                        "message_id": message_id,
                                        "detected_object_class": det[
                                            "detected_object_class"
                                        ],
                                        "confidence_score": det["confidence_score"],
                                        "detection_timestamp": datetime.now().isoformat(),
                                    }
                                )
                            processed_image_paths.add(image_full_path)
                        else:
                            if not os.path.exists(image_full_path):
                                logger.debug(
                                    f"Image file not found for message {message_id} at {image_full_path}"
                                )
                            elif not image_full_path.lower().endswith(
                                (".png", ".jpg", ".jpeg")
                            ):
                                logger.debug(
                                    f"Skipping non-image file for message {message_id}: {image_full_path}"
                                )
            except Exception as e:
                logger.error(f"Error reading or processing JSON file {json_path}: {e}")

    # Save all detection results to a single JSON file
    output_filename = (
        f"yolo_detections_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.json"
    )
    output_file_path = os.path.join(YOLO_OUTPUT_DIR, output_filename)

    with open(output_file_path, "w", encoding="utf-8") as f:
        json.dump(all_detection_results, f, ensure_ascii=False, indent=4)

    logger.info(f"YOLO detection results saved to: {output_file_path}")
    logger.info("YOLO object detection pipeline finished.")


if __name__ == "__main__":
    run_detection_pipeline()
