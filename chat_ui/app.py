import os
import sys
import re
import random

# ensure project root on PYTHONPATH
PROJECT_ROOT = os.path.abspath(os.path.join(__file__, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, request, jsonify, render_template
from common.db_client import DBClient
from common.spell_corrector import SpellCorrector
from common.paraphraser import Paraphraser
from common.config import TOP_K

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static")
)

db = DBClient()
speller = SpellCorrector()
paraphraser = Paraphraser()

# Define greeting patterns and responses
def is_greeting(message):
    # Convert to lowercase for case-insensitive matching
    msg = message.lower()

    # English greetings
    english_greetings = [
        r'\b(hi|hello|hey|greetings|howdy)\b',
        r'\bgood\s*(morning|afternoon|evening|day)\b',
        r'\bhow\s*(are\s*you|is\s*it\s*going|are\s*things)\b',
        r'\bwhat[\'\']*s\s*up\b',
        r'\bnice\s*to\s*(meet|see)\s*you\b'
    ]

    # Hindi greetings
    hindi_greetings = [
        r'\b(namaste|namaskar|नमस्ते|नमस्कार)\b',
        r'\b(kaise\s*ho|कैसे\s*हो)\b',
        r'\b(aap\s*kaise\s*hain|आप\s*कैसे\s*हैं)\b',
        r'\b(shubh\s*din|शुभ\s*दिन)\b',
        r'\b(suprabhat|सुप्रभात)\b',
        r'\b(shubh\s*prabhat|शुभ\s*प्रभात)\b'
    ]

    # Thank you expressions
    thank_you = [
        r'\b(thank\s*you|thanks|thank\s*you\s*very\s*much|thanks\s*a\s*lot)\b',
        r'\b(dhanyavaad|धन्यवाद|shukriya|शुक्रिया)\b'
    ]

    # Check if message matches any greeting pattern
    for pattern in english_greetings + hindi_greetings:
        if re.search(pattern, msg):
            return "greeting"

    for pattern in thank_you:
        if re.search(pattern, msg):
            return "thanks"

    return None

def get_greeting_response(greeting_type, msg):
    # For greetings, respond with the same greeting and then add information about the school
    if greeting_type == "greeting":
        # Check which greeting was used and respond with the same
        msg_lower = msg.lower()

        if re.search(r'\b(namaste|namaskar|नमस्ते|नमस्कार)\b', msg_lower):
            return "Namaste! I am a chatbot for G.D. Goenka Public School, Vasant Kunj. You can ask me any questions about our school."

        elif re.search(r'\b(kaise\s*ho|कैसे\s*हो|aap\s*kaise\s*hain|आप\s*कैसे\s*हैं)\b', msg_lower):
            return "Main badiya hoon! I am a chatbot for G.D. Goenka Public School, Vasant Kunj. You can ask me any questions about our school."

        elif re.search(r'\bgood\s*morning\b', msg_lower):
            return "Good morning! I am a chatbot for G.D. Goenka Public School, Vasant Kunj. You can ask me any questions about our school."

        elif re.search(r'\bgood\s*afternoon\b', msg_lower):
            return "Good afternoon! I am a chatbot for G.D. Goenka Public School, Vasant Kunj. You can ask me any questions about our school."

        elif re.search(r'\bgood\s*evening\b', msg_lower):
            return "Good evening! I am a chatbot for G.D. Goenka Public School, Vasant Kunj. You can ask me any questions about our school."

        elif re.search(r'\b(hi|hello)\b', msg_lower):
            return "Hi! I am a chatbot for G.D. Goenka Public School, Vasant Kunj. You can ask me any questions about our school."

        elif re.search(r'\bhey\b', msg_lower):
            return "Hey there! I am a chatbot for G.D. Goenka Public School, Vasant Kunj. You can ask me any questions about our school."

        # Default greeting response
        return "Hello! I am a chatbot for G.D. Goenka Public School, Vasant Kunj. You can ask me any questions about our school."

    elif greeting_type == "thanks":
        return "You're welcome! I am here to help with any questions about G.D. Goenka Public School, Vasant Kunj."

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    msg = data.get("message", "").strip()
    if not msg:
        return jsonify({"error": "empty message"}), 400

    # Check if the message is a greeting or thank you
    greeting_type = is_greeting(msg)
    if greeting_type:
        # Return a custom greeting response
        return jsonify({
            "question": msg,
            "corrected_query": msg,  # No need to correct greetings
            "answer": get_greeting_response(greeting_type, msg),
            "distance": 0.0,  # Perfect match
            "source": "Greeting Handler"
        })

    # 1) Spell‐correct the input
    corrected = speller.correct(msg)

    # 2) Semantic search on corrected query
    col = db.get_or_create_collection("delhi")
    results = col.query(
        query_texts=[corrected],
        n_results=TOP_K,
        include=["metadatas", "distances"]
    )

    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    # 3) If NO hits, fallback
    if not metadatas:
        return jsonify({
            "question": msg,
            "corrected_query": corrected,
            "answer": "Sorry, I don't have an answer for that. Please ask me something about G.D. Goenka Public School.",
            "distance": None,
            "source": ""
        })

    # 4) Otherwise always answer the top hit
    best_meta = metadatas[0]
    best_dist = distances[0]
    answer = best_meta.get("answer", "")

    # 5) Paraphrase for style/tone
    paraphrased = paraphraser.paraphrase(answer)

    return jsonify({
        "question": msg,
        "corrected_query": corrected,
        "answer": paraphrased,
        "distance": best_dist,
        "source": best_meta.get("source", "")
    })

if __name__ == "__main__":
    app.run(port=8001, debug=True)

