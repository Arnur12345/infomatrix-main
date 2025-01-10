import queue
import time

from common.person import Person
from common.service import ServiceBase

from .model import PoseModel


class PoseEstimationService(ServiceBase):
    def __init__(self, name, input_queue, output_queue, model_path):
        super().__init__(name)
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.model_path = model_path

    def run(self):
        self.model = PoseModel(self.model_path)
        self.logger.info("Starting pose estimation service.")

        while self.running.is_set():  # Check the Event flag
            start_time = time.time()

            if not self.input_queue.empty():
                # Run pose estimation model on the frame's image
                frame_data = self.input_queue.get()
                frame = frame_data.image
                poses = self.model.get_poses(frame)

                # Add detected poses to the FrameData
                for bbox, keypoints, confidence in poses:
                    person = Person(
                        confidence=confidence, bbox=bbox, keypoints=keypoints
                    )  # Assuming confidence is always 1.0 here
                    frame_data.add_person(person)

                # Push the processed FrameData with poses to the output queue
                self.output_queue.put(frame_data)
                end_time = time.time()
                self.logger.info(f"Pose estimation processed in {end_time - start_time:.3f} seconds.")

        self.logger.info("Pose estimation service stopped gracefully.")
