from collections import deque
import base64
import numpy as np
import cv2

MIN_SEQUENCE_LENGTH = 5

class FrameBuffer:
    def __init__(self, max_size=16):
        self.buffer = deque(maxlen=max_size)

    def add_frame(self, frame):
        self.buffer.append(frame)

    def get_frames(self):
        if len(self.buffer) < MIN_SEQUENCE_LENGTH:
            return []
        
        return list(self.buffer)

    def clear(self):
        self.buffer.clear()


def decode_frame(frameData):
    try:
        frameData = frameData.split(",")[1]
        frame_bytes = base64.b64decode(frameData)
        np_arr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return frame
    except Exception as e:
        print(f"Error decoding frame: {e}")
        return None

def decode_image_file(image):
    nparr = np.frombuffer(image, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return frame