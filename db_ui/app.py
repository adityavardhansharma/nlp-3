import os
import sys
import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for

# Ensure project root on PYTHONPATH
PROJECT_ROOT = os.path.abspath(os.path.join(__file__, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from db_ui.modules.admin_core import (
    list_collections,
    get_all_records,
    search_by_similarity,
    get_collection_stats
)

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static")
)

@app.context_processor
def inject_now():
    return {"now": datetime.datetime.now()}

@app.route("/")
def index():
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    cols = list_collections()
    stats = {c: get_collection_stats(c) for c in cols}
    return render_template(
        "dashboard.html",
        collections=cols,
        stats=stats
    )

@app.route("/collection/<collection_name>")
def collection_view(collection_name):
    cols = list_collections()
    return render_template(
        "collection.html",
        collection=collection_name,
        collections=cols,
        active_collection=collection_name
    )

@app.route("/search")
def search_page():
    cols = list_collections()
    sel = request.args.get("collection", cols[0] if cols else "")
    return render_template(
        "search.html",
        collections=cols,
        selected=sel,
        active_collection=sel
    )

@app.route("/api/records", methods=["POST"])
def records():
    payload = request.json or {}
    recs = get_all_records(
        payload.get("collection", ""),
        payload.get("page", 1),
        payload.get("limit", 10),
        payload.get("filters", {}),
        payload.get("include_fields", ["documents", "metadatas"])
    )
    return jsonify(recs)

@app.route("/api/search", methods=["POST"])
def search():
    payload = request.json or {}
    res = search_by_similarity(
        payload.get("collection", ""),
        payload.get("query", ""),
        payload.get("n_results", payload.get("limit", 5)),
        payload.get("include", payload.get("include_fields",
                                          ["documents", "metadatas", "distances"]))
    )
    return jsonify(res)

@app.route("/fix-misspellings/<collection_name>")
def fix_misspellings(collection_name):
    return jsonify({
        "success": True,
        "message": f"Misspellings fixed in collection {collection_name}"
    })

if __name__ == "__main__":
    app.run(port=8000, debug=True)
