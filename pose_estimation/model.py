import cv2
import numpy as np
import onnxruntime as ort  # type: ignore
from constants import PoseEstimationServiceConstants

from kit.box_utils import non_max_suppression


class PoseModel:
    def __init__(self, model_path):
        self.session = ort.InferenceSession(model_path, providers=PoseEstimationServiceConstants.EXECUTION_PROVIDERS)
        self.input_w = PoseEstimationServiceConstants.INPUT_W  # Model input width
        self.input_h = PoseEstimationServiceConstants.INPUT_H  # Model input height

    def preprocess(self, frame):
        """Resize image to model input size, keeping the aspect ratio."""
        original_h, original_w = frame.shape[:2]

        # Compute the scaling factor to fit the image within input_w x input_h
        scale_w = self.input_w / original_w
        scale_h = self.input_h / original_h
        scale = min(scale_w, scale_h)

        # Resize the image while maintaining aspect ratio
        new_w = round(original_w * scale)
        new_h = round(original_h * scale)
        resized_frame = cv2.resize(frame, (new_w, new_h))

        # Pad the resized image to match the exact input size
        pad_w = (self.input_w - new_w) // 2
        pad_h = (self.input_h - new_h) // 2
        padded_frame = cv2.copyMakeBorder(
            resized_frame, pad_h, pad_h, pad_w, pad_w, cv2.BORDER_CONSTANT, value=(0, 0, 0)
        )

        # Keep scaling and padding info for bounding box adjustment
        self.scale = scale
        self.pad_w = pad_w
        self.pad_h = pad_h

        # Normalize and prepare for model input
        rgb_img = cv2.cvtColor(padded_frame, cv2.COLOR_BGR2RGB)
        normalized_img = rgb_img.astype(np.float32) / 255.0
        chw_img = np.transpose(normalized_img, (2, 0, 1))
        input_data = np.expand_dims(chw_img, axis=0)
        return input_data

    def predict(self, input_data):
        input_name = self.session.get_inputs()[0].name
        outputs = self.session.run(None, {input_name: input_data})
        return outputs[0][0]

    def get_poses(self, frame):
        preprocessed_frame = self.preprocess(frame)
        output = self.predict(preprocessed_frame)

        bboxes = []
        confidences = []
        all_keypoints = []

        # Collect all bounding boxes and keypoints
        for i in range(output.shape[1]):
            detection = output[:, i]
            confidence = detection[4]
            if confidence > PoseEstimationServiceConstants.BBOX_CONF_THRESHOLD:
                xywh = detection[:4]
                x, y, w, h = xywh

                # Adjust bounding box back to the original image scale
                x_min = (x - w / 2 - self.pad_w) / self.scale
                y_min = (y - h / 2 - self.pad_h) / self.scale
                x_max = (x + w / 2 - self.pad_w) / self.scale
                y_max = (y + h / 2 - self.pad_h) / self.scale
                bbox = [int(x_min), int(y_min), int(x_max), int(y_max)]

                # Collect bounding boxes and confidences for NMS
                bboxes.append(bbox)
                confidences.append(float(confidence))

                # Adjust keypoints back to the original image scale
                keypoints = detection[5:56].reshape(-1, 3)
                for keypoint in keypoints:
                    keypoint[0] = (keypoint[0] - self.pad_w) / self.scale
                    keypoint[1] = (keypoint[1] - self.pad_h) / self.scale

                all_keypoints.append((bbox, keypoints, float(confidence)))

        # Apply NMS
        indices = non_max_suppression(bboxes, confidences)
        filtered_keypoints = [all_keypoints[i] for i in indices]

        return filtered_keypoints
