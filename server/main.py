from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from starlette.websockets import WebSocketState
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from landmark_extracter import extract_landmarks, process_frame
from word_level_model import load_word_model, predict_word_gloss
from sentence_level_model import load_sentence_model, predict_sentence_gloss
from text_language_generator import generate_continue_text, GlossBuffer, create_text_buffer
from frame_handler import FrameBuffer, decode_frame, decode_image_file

app = FastAPI()

# CORS Handler
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

word_model = load_word_model('saved_models/word_level_model_states_v3.pth')
sentence_model = load_sentence_model('saved_models/sentence_level_model_states_v3.pth')

thres_word_conf = 0.99
thres_sentence_conf = 0.9


def gloss_prediction(frameData, frame_buffer, gloss_buffer):
    """Receives frames, predicts glosses, and fills buffer."""
    try:
        frame = decode_frame(frameData)

        if frame is None:
            return {"status": "error", "message": "Invalid frame data"}

        landmarks = extract_landmarks(frame)

        frame_buffer.add_frame(landmarks)

        word_gloss, word_conf = predict_word_gloss(word_model, landmarks)

        frame_seq = frame_buffer.get_frames()
        sentence_gloss, sentence_conf = predict_sentence_gloss(sentence_model, frame_seq)

        if word_conf >= thres_word_conf:
            gloss_buffer.append_gloss(word_gloss)

        if sentence_conf >= thres_sentence_conf:
            gloss_buffer.append_gloss(sentence_gloss)

        # text = generate_continue_text(text_buffer, gloss_buffer)
        # text = word_gloss + " " + sentence_gloss

        result = {
            "word_confidence": word_conf,
            "sentence_confidence": sentence_conf
        }

        return {"status": "success", "result": result}
    
    except Exception as e:
        print(f"Error Processing Frame: {e}")
        return {"status": "error", "message": str(e)}


def text_generation(gloss_buffer, text_buffer):
    """Reads glosses and generates text asynchronously."""
    try:
        gen_text = generate_continue_text(gloss_buffer, text_buffer)

        if gen_text:
            text_buffer.extend(gen_text.split())

        return {"status": "success", "result": {"text": gen_text}}

    except Exception as e:
        print(f"Error Generating Text: {e}")
        return {"status": "error", "message": str(e)}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")

    frame_buffer = FrameBuffer(max_size=40)
    gloss_buffer = GlossBuffer()
    text_buffer = create_text_buffer()

    async def gloss_prediction_loop(websocket, frame_buffer, gloss_buffer):
        async for frame_data in websocket.iter_text():
            res = gloss_prediction(frame_data, frame_buffer, gloss_buffer)
            await websocket.send_json(res)

    async def text_generation_loop(websocket, gloss_buffer, text_buffer):
        while websocket.client_state == WebSocketState.CONNECTED:
            await asyncio.sleep(1.5)  # Check every second

            if websocket.client_state == WebSocketState.DISCONNECTED:
                break
            
            res = text_generation(gloss_buffer, text_buffer)

            if websocket.client_state == WebSocketState.DISCONNECTED:
                break

            await websocket.send_json(res)

    producer_task = asyncio.create_task(gloss_prediction_loop(websocket, frame_buffer, gloss_buffer))
    consumer_task = asyncio.create_task(text_generation_loop(websocket, gloss_buffer, text_buffer))

    try:
        await asyncio.gather(producer_task, consumer_task)
    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        producer_task.cancel()
        consumer_task.cancel()


@app.post('/upload-image')
async def upload_image(image: UploadFile = File(...)):
    try:
        content = await image.read()
        
        frame = decode_image_file(content)
        landmarks = extract_landmarks(frame)
        word_gloss, word_conf = predict_word_gloss(word_model, landmarks)

        response = {
            "text": word_gloss.lower() if word_conf >= thres_word_conf else "",
            "word_confidence": word_conf,
        }

        return {"status": "success", "result": response}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}