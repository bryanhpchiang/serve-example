import asyncio
from ray import serve
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import time
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

app = FastAPI()


@serve.deployment(num_replicas=10)
class Inference:
    def __init__(self):
        # sample model
        id2label = {0: "NEGATIVE", 1: "POSITIVE"}
        label2id = {"NEGATIVE": 0, "POSITIVE": 1}
        self.tokenizer = AutoTokenizer.from_pretrained(
            "distilbert-base-uncased")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "distilbert-base-uncased", num_labels=2, id2label=id2label, label2id=label2id
        )
        print("Model loaded.")

    def __call__(self, text: str) -> str:
        # model is so small we just run it on CPU
        start = time.time()
        with torch.no_grad():
            inputs = self.tokenizer(text, return_tensors="pt")
            logits = self.model(**inputs).logits.tolist()
            print("[WORKER] Took {} seconds to compute logits.".format(
                time.time() - start))
            return logits


@serve.deployment(num_replicas=1, route_prefix="/")
@serve.ingress(app)
class Ingress:
    def __init__(self, handle):
        self._handle = handle

    def inference(self, text):
        with torch.no_grad():
            inputs = self.tokenizer(text, return_tensors="pt")
            return self.model(**inputs).logits.tolist()

    async def _process(self, data, ws):
        start = time.time()
        ref = await self._handle.remote(data["text"])
        logits = await ref
        print("[INGRESS] Took {} seconds to complete request {}.".format(
            time.time() - start, data["id"]))
        await ws.send_text(json.dumps({
            "id": data["id"],
            "start": data["start"],
            "logits": logits
        }))

    @app.websocket("/")
    async def process(self, ws: WebSocket):
        await ws.accept()
        try:
            while True:
                text = await ws.receive_text()
                asyncio.ensure_future(self._process(json.loads(text), ws))
        except WebSocketDisconnect:
            print("Client disconnected.")


entrypoint = Ingress.bind(Inference.bind())
serve.run(entrypoint)

while True:
    pass
