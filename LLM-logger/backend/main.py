from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import requests
import json
import os
import time 

from logger import log_llm_interaction
from feedback import log_feedback


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "granite3.2:8b"


class PromptRequest(BaseModel):
    prompt: str


class FeedbackRequest(BaseModel):
    response_id: str
    rating: str
    comment: str = ""


def ensure_data_folder():
    if not os.path.exists("../data"):
        os.makedirs("../data")


@app.post("/generate")
def generate(request: PromptRequest):

    ensure_data_folder()

    def stream():
        payload = {
            "model": MODEL_NAME,
            "prompt": request.prompt,
            "stream": True
        }

        try:
            start_time = time.time()   # ✅ START TIMER

            response = requests.post(
                OLLAMA_URL,
                json=payload,
                stream=True,
                timeout=60
            )
            response.raise_for_status()

            full_response = ""

            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode("utf-8"))
                        token = chunk.get("response", "")
                        full_response += token
                        yield token
                    except json.JSONDecodeError:
                        continue

            latency = round((time.time() - start_time) * 1000, 2)  # ✅ END TIMER

            log = log_llm_interaction(
                request.prompt,
                full_response,
                MODEL_NAME,
                latency
            )

            yield f"\n\n[ID:{log['id']}]"

        except requests.exceptions.RequestException as e:
            yield f"\n[ERROR]: Unable to reach model → {str(e)}"

    return StreamingResponse(stream(), media_type="text/plain")


@app.post("/feedback")
def feedback(req: FeedbackRequest):
    try:
        log_feedback(req.response_id, req.rating, req.comment)
        return {"message": "Feedback saved"}
    except ValueError as e:
        return {"error": str(e)}