#!/usr/bin/env python3
import argparse
from common.db_client import DBClient
from common.config import JSONL_PATH

def main():
    p = argparse.ArgumentParser(
        description="Ingest a JSONL into Chroma")
    p.add_argument(
        "--jsonl", "-j",
        default=JSONL_PATH,
        help="Path to JSONL file")
    p.add_argument(
        "--collection", "-c",
        required=True,
        help="Chroma collection name")
    args = p.parse_args()

    db = DBClient()
    col = db.ingest_jsonl(args.jsonl, args.collection)
    print(f"Ingested {col.count()} records into collection `{args.collection}`")

if __name__ == "__main__":
    main()
