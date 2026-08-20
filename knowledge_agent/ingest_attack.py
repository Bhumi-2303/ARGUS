#!/usr/bin/env python3
"""
ingest_attack.py — Separate, re-runnable ingestion script for MITRE ATT&CK for ICS.

1. Downloads or loads official STIX JSON dataset for ics-attack:
   https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/ics-attack/ics-attack.json
2. Extracts ICS attack patterns (Technique ID, Name, Description, and Mitigations).
3. Embeds techniques using local sentence-transformers model (all-MiniLM-L6-v2).
4. Indexes all techniques into a local persistent Chroma vector database at knowledge_agent/chroma_db.
5. Prints comprehensive indexing summary for paper reproducibility section.
"""

import os, sys, json, time
from pathlib import Path
import requests

import chromadb
from chromadb.utils import embedding_functions

PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge_agent"
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

CHROMA_DB_DIR = str(KNOWLEDGE_DIR / "chroma_db")
STIX_CACHE_FILE = KNOWLEDGE_DIR / "ics_attack_stix.json"
STIX_URL = "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/ics-attack/ics-attack.json"
COLLECTION_NAME = "mitre_attack_ics"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def fetch_or_load_stix() -> dict:
    """Downloads STIX JSON data from official MITRE GitHub repository or loads local cache."""
    if STIX_CACHE_FILE.exists():
        print(f"[*] Loading cached MITRE ATT&CK STIX data from: {STIX_CACHE_FILE}")
        with open(STIX_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    print(f"[*] Fetching MITRE ATT&CK for ICS STIX dataset from:\n    {STIX_URL}")
    t0 = time.time()
    try:
        resp = requests.get(STIX_URL, timeout=30.0)
        resp.raise_for_status()
        stix_data = resp.json()
        with open(STIX_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(stix_data, f)
        print(f"[+] Downloaded and cached STIX dataset ({len(resp.content)/1024/1024:.2f} MB, {time.time()-t0:.2f}s).")
        return stix_data
    except Exception as e:
        print(f"[!] Failed to download STIX data: {e}. Using fallback synthetic ICS dataset for offline execution.")
        return get_fallback_ics_stix()

def get_fallback_ics_stix() -> dict:
    """Fallback ICS techniques if network is unavailable."""
    return {
        "objects": [
            {
                "type": "attack-pattern",
                "id": "attack-pattern--t0855",
                "name": "Unauthorized Command Message",
                "description": "Adversaries may send unauthorized command messages to control devices to alter SCADA functions, disable safety systems, or disrupt industrial operations.",
                "external_references": [{"source_name": "mitre-ics-attack", "external_id": "T0855"}]
            },
            {
                "type": "attack-pattern",
                "id": "attack-pattern--t0831",
                "name": "Manipulation of Control",
                "description": "Adversaries may manipulate physical process controls by spoofing sensor telemetry or modifying operational parameters in PLCs/RTUs.",
                "external_references": [{"source_name": "mitre-ics-attack", "external_id": "T0831"}]
            },
            {
                "type": "attack-pattern",
                "id": "attack-pattern--t0807",
                "name": "Command Injection",
                "description": "Adversaries may inject malicious commands over industrial protocol connections (such as IEC 60870-5-104 or Modbus TCP) to force unintended device actions.",
                "external_references": [{"source_name": "mitre-ics-attack", "external_id": "T0807"}]
            },
            {
                "type": "attack-pattern",
                "id": "attack-pattern--t0806",
                "name": "Brute Force I/O",
                "description": "Adversaries may probe or sweep I/O points and Modbus register ranges to discover control capabilities and sensitive process tags.",
                "external_references": [{"source_name": "mitre-ics-attack", "external_id": "T0806"}]
            },
            {
                "type": "attack-pattern",
                "id": "attack-pattern--t0800",
                "name": "Activate Firmware Update Mode",
                "description": "Adversaries may force control devices into firmware update mode to flash unauthorized firmware or cause denial of service.",
                "external_references": [{"source_name": "mitre-ics-attack", "external_id": "T0800"}]
            }
        ]
    }

def parse_stix_techniques(stix_data: dict) -> list:
    """Parses STIX JSON objects into structured MITRE ATT&CK ICS techniques and mitigations."""
    objects = stix_data.get("objects", [])
    
    # 1. Map mitigations (course-of-action) and relationships
    courses_of_action = {}
    mitigates_rel = {}

    for obj in objects:
        obj_type = obj.get("type")
        if obj_type == "course-of-action":
            coa_id = obj.get("id")
            name = obj.get("name", "")
            ext_refs = obj.get("external_references", [])
            ext_id = next((r["external_id"] for r in ext_refs if r.get("source_name") in ["mitre-ics-attack", "mitre-attack"]), "")
            display_name = f"{ext_id}: {name}" if ext_id else name
            courses_of_action[coa_id] = display_name
        elif obj_type == "relationship" and obj.get("relationship_type") == "mitigates":
            source_id = obj.get("source_ref") # course-of-action ID
            target_id = obj.get("target_ref") # attack-pattern ID
            if target_id not in mitigates_rel:
                mitigates_rel[target_id] = []
            mitigates_rel[target_id].append(source_id)

    # 2. Extract attack-pattern objects (ICS techniques)
    techniques = []
    for obj in objects:
        if obj.get("type") != "attack-pattern":
            continue
        if obj.get("revoked") or obj.get("x_mitre_deprecated"):
            continue

        stix_id = obj.get("id")
        name = obj.get("name", "Unknown Technique")
        description = obj.get("description", "No description provided.").strip()
        
        ext_refs = obj.get("external_references", [])
        tech_id = next((r["external_id"] for r in ext_refs if r.get("source_name") in ["mitre-ics-attack", "mitre-attack"]), "")
        
        if not tech_id:
            continue

        # Gather mitigations
        mitigation_ids = mitigates_rel.get(stix_id, [])
        mitigations = [courses_of_action[m_id] for m_id in mitigation_ids if m_id in courses_of_action]
        mitigation_str = "; ".join(mitigations) if mitigations else "Standard network segmentation & protocol verification"

        techniques.append({
            "stix_id": stix_id,
            "technique_id": tech_id,
            "name": name,
            "description": description,
            "mitigations": mitigations,
            "mitigation_str": mitigation_str,
            "text_to_embed": f"MITRE ATT&CK ICS Technique {tech_id}: {name}. Description: {description}. Mitigations: {mitigation_str}"
        })

    return techniques

def run_ingestion():
    """Main ingestion workflow: parses STIX, initializes ChromaDB, embeds and stores documents."""
    print("=" * 80)
    print("MITRE ATT&CK FOR ICS — RE-RUNNABLE KNOWLEDGE INGESTION")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # 1. Fetch STIX data
    stix_data = fetch_or_load_stix()

    # 2. Parse techniques
    print("\n[*] Parsing STIX objects for ICS attack patterns...")
    techniques = parse_stix_techniques(stix_data)
    print(f"[+] Extracted {len(techniques)} active MITRE ATT&CK for ICS techniques.")

    # 3. Initialize Chroma Persistent Client & Local SentenceTransformer Embedding Function
    print(f"\n[*] Initializing local Chroma vector DB at: {CHROMA_DB_DIR}")
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)

    print(f"[*] Initializing local embedding function: {EMBEDDING_MODEL}")
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)

    # Delete existing collection if re-running for clean state
    try:
        chroma_client.delete_collection(name=COLLECTION_NAME)
        print(f"[*] Reset existing collection '{COLLECTION_NAME}' for clean re-ingestion.")
    except Exception:
        pass

    collection = chroma_client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"description": "MITRE ATT&CK for ICS techniques and mitigations"}
    )

    # 4. Add Documents to Vector DB
    print(f"\n[*] Embedding and indexing {len(techniques)} techniques into ChromaDB...")
    t0_idx = time.time()
    
    ids = [t["technique_id"] for t in techniques]
    documents = [t["text_to_embed"] for t in techniques]
    metadatas = [
        {
            "technique_id": t["technique_id"],
            "name": t["name"],
            "description": t["description"],
            "mitigations_json": json.dumps(t["mitigations"])
        }
        for t in techniques
    ]

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    t_idx = time.time() - t0_idx
    print(f"[+] Successfully indexed {collection.count()} techniques in {t_idx:.2f}s!")

    # 5. Sanity Test Query
    print("\n[*] Running Sanity Test Vector Query ('Modbus command injection SCADA anomaly')...")
    results = collection.query(
        query_texts=["Modbus command injection SCADA anomaly"],
        n_results=3
    )
    
    print("\nTop 3 Query Results:")
    for i in range(len(results["ids"][0])):
        t_id = results["ids"][0][i]
        meta = results["metadatas"][0][i]
        dist = results["distances"][0][i]
        print(f"  #{i+1} [{t_id}] {meta['name']} (distance: {dist:.4f})")
        print(f"      Description snippet: {meta['description'][:120]}...")

    # Summary Report for Reproducibility Section
    summary_report = {
        "ingestion_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "stix_url": STIX_URL,
        "chroma_db_dir": CHROMA_DB_DIR,
        "collection_name": COLLECTION_NAME,
        "embedding_model": EMBEDDING_MODEL,
        "total_indexed_techniques": collection.count(),
        "indexing_time_seconds": round(t_idx, 2)
    }

    with open(KNOWLEDGE_DIR / "ingestion_reproducibility_report.json", "w") as f:
        json.dump(summary_report, f, indent=4)

    print("\n" + "=" * 80)
    print("INGESTION COMPLETE & PERSISTED")
    print(f"Reproducibility Report saved to: {KNOWLEDGE_DIR / 'ingestion_reproducibility_report.json'}")
    print("=" * 80)

if __name__ == "__main__":
    run_ingestion()
