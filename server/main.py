from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from landmark_extracter import extract_landmarks, process_frame
from word_level_model import load_word_model, predict_word_gloss
from sentence_level_model import load_sentence_model, predict_sentence_gloss
from text_language_generator import generate_continue_text, GlossBuffer, create_text_buffer
from frame_buffer import FrameBuffer

import base64
import cv2
import numpy as np

app = FastAPI()

word_model = load_word_model('saved_models/word_level_model_states_v3.pth')
sentence_model = load_sentence_model('saved_models/sentence_level_model_states_v3.pth')

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")

    try:
        frame_buffer = FrameBuffer(max_size=40)
        gloss_buffer = GlossBuffer()
        text_buffer = create_text_buffer()

        while True:
            frameData = await websocket.receive_text()
            frame = decode_frame(frameData)

            if frame is not None:
                landmarks = extract_landmarks(frame)

                frame_buffer.add_frame(landmarks)

                word_gloss, word_conf = predict_word_gloss(word_model, landmarks)

                frame_seq = frame_buffer.get_frames()
                sentence_gloss, sentence_conf = predict_sentence_gloss(sentence_model, frame_seq)
                gloss_buffer.append_gloss(sentence_gloss)

                response = {
                    "word_gloss": word_gloss,
                    "word_confidence": word_conf,
                    "sentence_gloss": sentence_gloss,
                    "sentence_confidence": sentence_conf,
                }

                await websocket.send_json({"status": "success", "result": response})

            else:
                await websocket.send_json({"status": "error", "message": "Failed to decode frame"})

    except WebSocketDisconnect:
        print("Client disconnected")
    
    except Exception as e:
        print(f"Error: {e}")
        # await websocket.send_json({"status": "error", "message": str(e)})


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