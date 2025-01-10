import base64
from uuid import uuid4

import cv2
import numpy as np


# Function to save encodings and names to a file
def save_encodings(filename, known_face_encodings, known_face_names):
    np.savez(filename, encodings=known_face_encodings, names=known_face_names)


# Function to load encodings and names from a file
def load_encodings(filename):
    data = np.load(filename)
    return data["encodings"], data["names"]


# Function to handle user input in a separate thread
def get_user_input():
    global name, new_face_detected
    name = input("New face detected, please enter Full Name: ")
    if len(name):
        new_face_detected = True
    else:
        print("Ignoring empty input")


def string_uuid() -> str:
    return str(uuid4())


def cv_image_to_base64(cv_image):
    _, buffer = cv2.imencode(".jpg", cv_image)  # Encode the NumPy array to JPG format
    base64_str = base64.b64encode(buffer).decode("utf-8")  # Convert to base64 string
    return base64_str


def numpy_image_to_base64(image: np.ndarray, format: str = "png") -> str:
    # Convert the NumPy array to an image format
    success, encoded_image = cv2.imencode(f".{format}", image)

    if not success:
        raise ValueError("Could not encode image")

    # Convert the encoded image to bytes
    image_bytes = encoded_image.tobytes()

    # Encode the bytes to Base64
    base64_encoded = base64.b64encode(image_bytes).decode("utf-8")

    return base64_encoded


def create_grid_image(frames, grid_size, cell_size):
    """
    Create a grid image from multiple frames.
    Parameters:
        frames (list): List of frames (images) from different cameras.
        grid_size (tuple): Size of the grid (rows, cols).
        cell_size (tuple): Size of each cell (width, height).
    Returns:
        grid_image (np.array): Final grid image containing all frames.
    """
    rows, cols = grid_size
    grid_image = np.zeros((cell_size[1] * rows, cell_size[0] * cols, 3), dtype=np.uint8)

    for idx, frame in enumerate(frames):
        if idx >= rows * cols:
            break  # Avoid placing frames outside the grid

        resized_frame = cv2.resize(frame, cell_size)
        row, col = divmod(idx, cols)

        grid_image[
            row * cell_size[1] : (row + 1) * cell_size[1],
            col * cell_size[0] : (col + 1) * cell_size[0],
        ] = resized_frame

    return grid_image
