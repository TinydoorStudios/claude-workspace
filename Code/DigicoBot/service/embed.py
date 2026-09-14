"""Local embeddings — bge-small-en-v1.5 via fastembed (ONNX, CPU, ~130 MB, 384 dims).

The model is downloaded once into /models (a docker volume) and loaded lazily on first use, so the
container starts fast and the health check doesn't wait on it.
"""
import threading

from settings import S

_model = None
_lock = threading.Lock()


def _get():
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                from fastembed import TextEmbedding
                _model = TextEmbedding(model_name=S.embed_model, cache_dir='/models')
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    return [v.tolist() for v in _get().embed(texts, batch_size=4)]


def embed_query(q: str) -> list[float]:
    return embed_texts([q])[0]
