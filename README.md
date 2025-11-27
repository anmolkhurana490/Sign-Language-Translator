# AI Powered Indian Sign Language Translator

A realtime system for continuous prediction of Indian Sign Language glosses (word-level) and generation of natural text using large language models (LLMs). The project performs continuous prediction from async camera frames via a FastAPI websocket server and a React.js client.

## Key features
- Continuous, low-latency prediction of sign glosses (word-level).
- LLM-based generation of fluent text from predicted gloss sequences.
- Server: FastAPI with websocket support for streaming asynchronous frames.
- Client: React.js front-end for camera capture and live display.
- Realtime-ready architecture optimized for continuous frame inputs.

## Performance (benchmarks)
- Overall word-level accuracy: 80%
- Accuracy on first 50 word classes: 92%

## Datasets Used
- [INCLUDE]: A large-scale dataset for Indian Sign Language Recognition.
    - Dataset: [https://zenodo.org/records/4010759](https://zenodo.org/records/4010759)
    - Paper: [https://dl.acm.org/doi/10.1145/3394171.3413528](https://dl.acm.org/doi/10.1145/3394171.3413528)
    - Github: [https://github.com/AI4Bharat/INCLUDE](https://github.com/AI4Bharat/INCLUDE)


## Project structure (example)
- /server — FastAPI websocket server, model loading, inference pipeline
- /client — React.js app for camera capture and websocket client
- /model_training — experiments and evaluation notebooks
- /saved_models — trained model checkpoints and tokenizer/label files
- /data — dataset metadata, splits, preprocessed data, ordered class lists

## Setup

Prerequisites
- Python 3.8+
- Node.js 14+
- GPU recommended for model inference/training

Server (FastAPI)
```bash
cd server
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

Client (React)
```bash
cd client
npm install
npm start
# opens at http://localhost:3000
```

## Docker Deployment
- Build Docker image:
```bash
docker build -t sign-language-translator-server .
```
- Run Docker container:
```bash
docker run -p 8000:8000 \
    --env-file .env \
    sign-language-translator-server
```
- Access FastAPI at http://localhost:8000 and websocket at ws://localhost:8000/ws/stream

## Websocket API (example)
- Endpoint: ws://<server-host>:8000/ws/stream
- Client -> Server: stream frames continuously (binary or JSON with base64 image)
    Example JSON message:
    {
        "frame_id": 123,
        "timestamp": 1670000000.0,
        "image_b64": "<base64-encoded-jpeg>"
    }
- Server -> Client: continuous predictions
    Example response:
    {
        "frame_id": 123,
        "gloss": "HELLO",
        "confidence": 0.92,
        "generated_text": "Hello, how are you?"
    }

Notes:
- The server accepts asynchronous frame inputs and returns incremental gloss predictions. The LLM post-processes gloss sequences into fluent text (can be batched or streamed).

## Tips for improvement
- Use temporal models (3D CNNs, I3D, Transformer encoders) for better continuous prediction.
- Add context windowing and smoothing for noisy frame-level predictions.
- Fine-tune LLM prompt/conditioning on gloss sequences to improve text generation.

## Contributing
- Fork, branch from main, open pull requests with clear descriptions.
- Include tests and update README for new features.

## Contact
For questions or collaboration, open an issue or contact the maintainers in the repository.