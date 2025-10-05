from collections import deque

MIN_SEQUENCE_LENGTH = 3

class FrameBuffer:
    def __init__(self, max_size=16):
        self.buffer = deque(maxlen=max_size)

    def add_frame(self, frame):
        self.buffer.append(frame)

    def get_frames(self):
        if len(self.buffer) < MIN_SEQUENCE_LENGTH:
            return None
        
        return list(self.buffer)

    def clear(self):
        self.buffer.clear()