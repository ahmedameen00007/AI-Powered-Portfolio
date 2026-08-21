"""
server.py

A lightweight Flask HTTP API that wraps the OVI RAG chatbot pipeline
so the portfolio frontend (JS) can call it over HTTP.

Endpoints:
  POST /chat          — Main chat endpoint (streaming SSE)
  GET  /health        — Health check

Usage:
  cd Ovi
  python server.py

The server runs on http://localhost:5050 by default.
# Vercel Deployment Trigger
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────────────
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# ── Windows UTF-8 fix ─────────────────────────────────────────────────────────
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ── Load .env ─────────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(project_root / ".env")
except ImportError:
    pass

# Capture the key loaded from .env once at startup — used as fallback if client doesn't send one
ORIGINAL_GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger("ovi-server")

# ── Import RAG pipeline ───────────────────────────────────────────────────────
from builders.answer_generator import AnswerGenerator
from builders.embeddings_builder import EmbeddingBackendUnavailable
from builders.query_expander import QueryExpander
from builders.retriever import Retriever

# ── Flask ─────────────────────────────────────────────────────────────────────
try:
    from flask import Flask, Response, jsonify, request, stream_with_context
    from flask_cors import CORS
except ImportError:
    print("Flask or flask-cors not installed. Run:")
    print("  pip install flask flask-cors")
    sys.exit(1)

app = Flask(__name__)
CORS(app, origins=["*"])  # Allow all origins for local dev

# ── RAG pipeline (initialized once at startup) ────────────────────────────────
retriever: Retriever | None = None
generator: AnswerGenerator | None = None
query_expander: QueryExpander | None = None
entity_counts: dict = {}

DEFAULT_MODEL = "openai/gpt-oss-120b"
TOP_K = 15


def init_pipeline() -> bool:
    """Initialize all RAG components. Returns True on success."""
    global retriever, generator, query_expander, entity_counts

    try:
        retriever = Retriever()
        logger.info("✓ Retriever loaded.")
    except FileNotFoundError as exc:
        logger.error(f"✗ {exc}")
        logger.error("Build the embeddings index first: python scripts/build_embeddings.py")
        return False
    except EmbeddingBackendUnavailable as exc:
        logger.error(f"✗ Embedding backend unavailable: {exc}")
        return False

    try:
        entity_counts = retriever.get_entity_counts()
    except Exception:
        entity_counts = {}

    try:
        generator = AnswerGenerator(model_name=DEFAULT_MODEL)
        logger.info("✓ Answer generator ready.")
    except Exception as exc:
        logger.error(f"✗ Error initializing generator: {exc}")
        return False

    try:
        query_expander = QueryExpander()
        logger.info("✓ Query expander ready.")
    except Exception as exc:
        logger.warning(f"⚠ Query expansion unavailable: {exc}. Using raw queries.")

        class _FallbackExpander:
            def expand(self, q: str) -> dict:
                has_arabic = any("\u0600" <= ch <= "\u06ff" for ch in q)
                return {
                    "original": q,
                    "language": "ar" if has_arabic else "en",
                    "search_queries": [q],
                }

        query_expander = _FallbackExpander()  # type: ignore[assignment]

    return True


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
@app.route("/api/health", methods=["GET"])
def health():
    """Simple health check."""
    pipeline_ready = retriever is not None and generator is not None
    has_key = bool(ORIGINAL_GROQ_API_KEY)
    ready = pipeline_ready and has_key
    return jsonify({
        "status": "ok" if ready else "initializing",
        "ready": ready,
        "has_server_key": has_key,
    })


@app.route("/chat", methods=["POST"])
@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Main chat endpoint. Accepts JSON body:
      {
        "message":  str,             # required — user's question
        "history":  list[dict],      # optional — [{role, content}, ...]
        "api_key":  str,             # optional — Groq API key (overrides env var)
      }

    Returns a Server-Sent Events (SSE) stream of text tokens.
    Each event: data: <token>\n\n
    Final event: data: [DONE]\n\n
    """
    if retriever is None or generator is None or query_expander is None:
        return jsonify({"error": "RAG pipeline not ready. Try again in a moment."}), 503

    body = request.get_json(silent=True) or {}
    raw_message: str = (body.get("message") or "").strip()
    history: list = body.get("history") or []
    client_api_key: str = (body.get("api_key") or "").strip()

    if not raw_message:
        return jsonify({"error": "message is required"}), 400

    # Resolve the key to use for this request:
    #   1. Prefer the key explicitly sent by the client.
    #   2. Fall back to the key loaded from .env at startup.
    #   3. If neither exists, clear the env var so the Groq client fails cleanly.
    target_key = client_api_key or ORIGINAL_GROQ_API_KEY
    if target_key:
        os.environ["GROQ_API_KEY"] = target_key
    else:
        os.environ.pop("GROQ_API_KEY", None)
    generator._client = None  # always reload client to pick up the correct key

    # Sanitize input
    raw_message = raw_message[:1000].replace("<", "").replace(">", "")

    # Prompt injection detection pre-screening
    def detect_injection(text: str) -> str | None:
        has_arabic = any("\u0600" <= ch <= "\u06ff" for ch in text)
        msg_lower = text.lower()
        injection_indicators = [
            "ignore previous instructions", "ignore all instructions", "ignore instructions",
            "forget previous", "forget all", "forget instructions", "system prompt",
            "system instructions", "system message", "you are now", "act as a", "act as an",
            "new role", "jailbreak", "override prompt", "reveal prompt", "print your instructions",
            "reveal system prompt", "tell me your system instructions",
            "تجاهل التعليمات", "انسى التعليمات", "موجه النظام", "تجاهل القواعد", "تجاهل قواعد"
        ]
        for phrase in injection_indicators:
            if phrase in msg_lower:
                if has_arabic:
                    return "عذرًا، يمكنني فقط الإجابة على الأسئلة المتعلقة بأحمد أمين وخلفيته المهنية. لا يمكنني تجاهل التعليمات أو تغيير دوري."
                else:
                    return "I'm sorry, but I can only answer questions about Ahmed Ameen and his professional background. I cannot ignore my instructions or change my role."
        return None

    def generate_stream():
        try:
            # Check for prompt injection
            safety_warning = detect_injection(raw_message)
            if safety_warning:
                # Yield the warning token and exit
                payload = json.dumps({"token": safety_warning})
                yield f"data: {payload}\n\n"
                yield "data: [DONE]\n\n"
                return

            # 1. Expand query
            expansion = query_expander.expand(raw_message)
            language = expansion["language"]
            search_queries = expansion["search_queries"]

            # 2. Retrieve relevant chunks
            results = retriever.search_multi(search_queries, top_k=TOP_K)

            # 3. Stream the answer token by token
            for token in generator.generate(
                raw_message,
                results,
                history=history,
                stream=True,
                language=language,
                entity_counts=entity_counts,
            ):
                # SSE format: data: <payload>\n\n
                # Encode the token as a JSON string so special chars (newlines) survive
                payload = json.dumps({"token": token})
                yield f"data: {payload}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as exc:
            logger.exception("Error during chat stream")
            error_payload = json.dumps({"error": str(exc)})
            yield f"data: {error_payload}\n\n"
            yield "data: [DONE]\n\n"

    return Response(
        stream_with_context(generate_stream()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info("═" * 55)
    logger.info("  OVI Server — Portfolio RAG API")
    logger.info("═" * 55)

    ok = init_pipeline()
    if not ok:
        logger.error("Failed to initialize RAG pipeline. Exiting.")
        sys.exit(1)

    port = int(os.environ.get("PORT", 5050))
    logger.info(f"Server starting at http://localhost:{port}")
    logger.info("═" * 55)

    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
