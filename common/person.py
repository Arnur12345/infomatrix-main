from dataclasses import dataclass, field

from .models import UserAccount


@dataclass
class Person:
    bbox: tuple[int, int, int, int]
    confidence: float
    keypoints: list[tuple[int, int, float]]
    track_id: int | None = None
    user: UserAccount | None = None
    face_bbox: tuple[int, int, int, int] | None = None
    face_confidence: float | None = None
    head_bbox: tuple[int, int, int, int] | None = None
    head_orientation: str | None = None

    def set_face(self, user: UserAccount, face_bbox: tuple[int, int, int, int], face_confidence: float):
        """
        Set face-specific attributes for the person.
        Parameters:
            user (UserAccount): Identified user for the detected face.
            face_bbox (tuple): Bounding box of the face in the frame (x_min, y_min, x_max, y_max).
            face_confidence (float): Confidence score of the face detection.
        """
        self.user = user
        self.face_bbox = face_bbox
        self.face_confidence = face_confidence

    def set_head(self, head_orientation: str, head_bbox: tuple[int, int, int, int]):
        """
        Set head-specific attributes for the person.
        Parameters:
            orientation (str): Face orientation.
            head_bbox (tuple): Bounding box of the head in the frame (x_min, y_min, x_max, y_max).
        """
        self.head_orientation = head_orientation
        self.head_bbox = head_bbox

    def __repr__(self):
        return (
            f"Person(bbox={self.bbox}, confidence={self.confidence}, track_id={self.track_id}, "
            f"user_name={self.user.user_name}, face_bbox={self.face_bbox}, face_confidence={self.face_confidence})"
        )
