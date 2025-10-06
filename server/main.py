from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

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

                if word_conf >= thres_word_conf:
                    gloss_buffer.append_gloss(word_gloss)

                if sentence_conf >= thres_sentence_conf:
                    gloss_buffer.append_gloss(sentence_gloss)

                # text = generate_continue_text(text_buffer, gloss_buffer)
                text = word_gloss + " " + sentence_gloss

                result = {
                    "word_confidence": word_conf,
                    "sentence_confidence": sentence_conf,
                    "text": text.lower(),
                }

                await websocket.send_json({"status": "success", "result": result})

            else:
                await websocket.send_json({"status": "error", "message": "Failed to decode frame"})

    except WebSocketDisconnect:
        print("Client disconnected")
    
    except Exception as e:
        print(f"Error: {e}")
        # await websocket.send_json({"status": "error", "message": str(e)})

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