import cv2
import numpy as np


def non_max_suppression(bboxes, confidences, threshold=0.8):
    """
    Apply Non-Maximum Suppression (NMS) to filter out overlapping bounding boxes.
    Parameters:
        bboxes (list): List of bounding boxes in [x_min, y_min, width, height] format.
        confidences (list): List of confidence scores for each bounding box.
        threshold (float): Overlap threshold for NMS.
    Returns:
        List of indices of the remaining bounding boxes after NMS.
    """
    indices = cv2.dnn.NMSBoxes(bboxes, confidences, score_threshold=0.0, nms_threshold=threshold)
    return indices.flatten() if len(indices) > 0 else []


def bbox_iou(box1, box2):
    """Calculate Intersection over Union (IoU) between two bounding boxes."""
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    x1_min, x1_max = x1, x1 + w1
    y1_min, y1_max = y1, y1 + h1
    x2_min, x2_max = x2, x2 + w2
    y2_min, y2_max = y2, y2 + h2

    inter_x_min = max(x1_min, x2_min)
    inter_y_min = max(y1_min, y2_min)
    inter_x_max = min(x1_max, x2_max)
    inter_y_max = min(y1_max, y2_max)

    inter_w = max(0, inter_x_max - inter_x_min)
    inter_h = max(0, inter_y_max - inter_y_min)
    inter_area = inter_w * inter_h

    box1_area = w1 * h1
    box2_area = w2 * h2

    union_area = box1_area + box2_area - inter_area
    return inter_area / union_area if union_area > 0 else 0


def bbox_distance(box1, box2):
    """Calculate the distance between the centers of two bounding boxes."""
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    center1 = np.array([x1 + w1 / 2, y1 + h1 / 2])
    center2 = np.array([x2 + w2 / 2, y2 + h2 / 2])
    return np.linalg.norm(center1 - center2)


def combine_boxes(box1, box2):
    """Return the smallest bounding box that contains both input boxes."""
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    x_min = min(x1, x2)
    y_min = min(y1, y2)
    x_max = max(x1 + w1, x2 + w2)
    y_max = max(y1 + h1, y2 + h2)

    return [x_min, y_min, x_max - x_min, y_max - y_min]


def merge_bboxes(bboxes, distance_thresh=0.2):
    """
    Merge overlapping or close bounding boxes.

    Parameters:
    - bboxes: List of bounding boxes in [x, y, w, h] format.
    - distance_thresh: The threshold distance proportional to the bbox size
      to consider two bboxes as close.

    Returns:
    - merged_bboxes: List of merged bounding boxes in [x, y, w, h] format.
    """

    merged = []
    while bboxes:
        current_box = bboxes.pop(0)
        has_merged = False

        for i in range(len(merged)):
            if bbox_iou(current_box, merged[i]) > 0 or bbox_distance(current_box, merged[i]) < distance_thresh * max(
                current_box[2], current_box[3]
            ):
                # Combine the boxes and update the merged list
                merged[i] = combine_boxes(current_box, merged[i])
                has_merged = True
                break

        if not has_merged:
            merged.append(current_box)

    return merged
