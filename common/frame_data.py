from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

import cv2
import numpy as np
from constants import PoseEstimationServiceConstants
from pose_estimation.pose_connections import POSE_CONNECTIONS

from .person import Person


@dataclass
class FrameData:
    image: np.ndarray
    index: int
    timestamp: datetime = field(default_factory=datetime.now)
    persons: list[Person] = field(default_factory=list)
    rois: list[tuple[int, int, int, int]] = field(default_factory=list)
    key_conf_th: float = PoseEstimationServiceConstants.KEYPOINT_CONF_THRESHOLD

    def add_person(self, person: Person):
        """Add a detected person to the frame."""
        self.persons.append(person)

    def draw_persons(self, scale_x=1, scale_y=1):
        """
        Draw bounding boxes and keypoints on the frame.
        Parameters:
            scale_x (float): Scale factor for x coordinates.
            scale_y (float): Scale factor for y coordinates.
        Returns:
            np.array: The image with bounding boxes and keypoints drawn.
        """
        frame = self.image.copy()

        for person in self.persons:
            bbox = person.bbox
            face_bbox = person.face_bbox
            user = person.user
            iou_track_id = person.track_id
            confidence = person.confidence
            keypoints = person.keypoints

            # Draw bounding box
            x_min, y_min, x_max, y_max = bbox
            x_min, x_max = int(x_min * scale_x), int(x_max * scale_x)
            y_min, y_max = int(y_min * scale_y), int(y_max * scale_y)
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 4)
            cv2.putText(
                frame, str(iou_track_id), (x_min + 6, y_min + 29), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1
            )

            # Draw keypoints
            if person.head_bbox:
                x_min, y_min, x_max, y_max = person.head_bbox
                orientation = person.head_orientation
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 0, 255), 4)
                cv2.putText(
                    frame, orientation, (x_min + 6, y_min + 29), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1
                )

            for x, y, keypoint_confidence in keypoints:
                if keypoint_confidence > self.key_conf_th:  # Only draw keypoints with high confidence
                    x, y = int(x * scale_x), int(y * scale_y)
                    cv2.circle(frame, (x, y), 3, (0, 0, 255), -1)

            # Draw connections
            for start, end in POSE_CONNECTIONS:
                if keypoints[start][2] > self.key_conf_th and keypoints[end][2] > self.key_conf_th:
                    pt1 = (int(keypoints[start][0] * scale_x), int(keypoints[start][1] * scale_y))
                    pt2 = (int(keypoints[end][0] * scale_x), int(keypoints[end][1] * scale_y))
                    cv2.line(frame, pt1, pt2, (255, 0, 0), 4)
            if face_bbox:
                x_min, y_min, x_max, y_max = face_bbox
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (255, 0, 0), 4)
                if person.user:
                    cv2.putText(
                        frame,
                        user.user_name + " " + str(confidence),
                        (x_min + 6, y_min + 29),
                        cv2.FONT_HERSHEY_DUPLEX,
                        0.7,
                        (255, 255, 255),
                        1,
                    )

        return frame

    def draw_person(self, user_id, scale_x=1, scale_y=1):
        """
        Draw bounding boxes and keypoints on the frame.
        Parameters:
            scale_x (float): Scale factor for x coordinates.
            scale_y (float): Scale factor for y coordinates.
        Returns:
            np.array: The image with bounding boxes and keypoints drawn.
        """
        frame = self.image.copy()

        for person in self.persons:
            person_user_id = ""
            if person.user:
                person_user_id = person.user.id
            if person_user_id == user_id:
                bbox = person.bbox
                face_bbox = person.face_bbox
                iou_track_id = person.track_id
                confidence = person.confidence
                keypoints = person.keypoints
                # Draw bounding box
                x_min, y_min, x_max, y_max = bbox
                x_min, x_max = int(x_min * scale_x), int(x_max * scale_x)
                y_min, y_max = int(y_min * scale_y), int(y_max * scale_y)
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 4)
                cv2.putText(
                    frame, str(iou_track_id), (x_min + 6, y_min + 29), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1
                )

                # Draw keypoints
                if person.head_bbox:
                    x_min, y_min, x_max, y_max = person.head_bbox
                    orientation = person.head_orientation
                    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 0, 255), 4)
                    cv2.putText(
                        frame, orientation, (x_min + 6, y_min + 29), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1
                    )

                for x, y, keypoint_confidence in keypoints:
                    if keypoint_confidence > self.key_conf_th:  # Only draw keypoints with high confidence
                        x, y = int(x * scale_x), int(y * scale_y)
                        cv2.circle(frame, (x, y), 3, (0, 0, 255), -1)

                # Draw connections
                for start, end in POSE_CONNECTIONS:
                    if keypoints[start][2] > self.key_conf_th and keypoints[end][2] > self.key_conf_th:
                        pt1 = (int(keypoints[start][0] * scale_x), int(keypoints[start][1] * scale_y))
                        pt2 = (int(keypoints[end][0] * scale_x), int(keypoints[end][1] * scale_y))
                        cv2.line(frame, pt1, pt2, (255, 0, 0), 4)
                if face_bbox:
                    x_min, y_min, x_max, y_max = face_bbox
                    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (255, 0, 0), 4)
                    if person.user:
                        cv2.putText(
                            frame,
                            person.user.user_name + " " + str(confidence),
                            (x_min + 6, y_min + 29),
                            cv2.FONT_HERSHEY_DUPLEX,
                            0.7,
                            (255, 255, 255),
                            1,
                        )

        return frame

    def get_image(self):
        """Return the image from the frame data."""
        return self.image

    def __repr__(self):
        return f"FrameData(timestamp={self.timestamp}, num_persons={len(self.persons)})"
