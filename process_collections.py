import os
import json
import fitz  # PyMuPDF
from datetime import datetime, timezone

# Settings
MAX_PAGES = 3
BASE_DIR = '.'

# Group-based itinerary suggestion logic (dummy logic)
def assign_day_rank(rank):
    if rank == 1 or rank == 2:
        return 1  # Day 1 - Cities, Stay
    elif rank == 3:
        return 2  # Day 2 - Food
    elif rank == 4:
        return 3  # Day 3 - Activities
    elif rank == 5:
        return 0  # General travel tips
    return (rank % 4) + 1

# Simple keyword extractor
def extract_keywords(text):
    words = [word.lower() for word in text.split() if len(word) > 4 and word.isalpha()]
    common = {}
    for w in words:
        common[w] = common.get(w, 0) + 1
    sorted_keywords = sorted(common.items(), key=lambda item: item[1], reverse=True)
    return [kw[0] for kw in sorted_keywords[:5]]

# PDF text extractor
def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        return [(i + 1, page.get_text().strip()) for i, page in enumerate(doc)]
    except Exception as e:
        print(f"[ERROR] Failed to process {pdf_path}: {e}")
        return []

# Main processor
def process_collection(collection_path):
    input_path = os.path.join(collection_path, "challenge1b_input.json")
    output_path = os.path.join(collection_path, "challenge1b_output.json")
    pdf_dir = os.path.join(collection_path, "PDFs")

    if not os.path.exists(input_path):
        print(f"[SKIP] No input JSON found in {collection_path}")
        return

    with open(input_path, "r") as f:
        data = json.load(f)

    metadata = {
        "input_documents": [doc["filename"] for doc in data["documents"]],
        "persona": data["persona"]["role"],
        "job_to_be_done": data["job_to_be_done"]["task"],
        "processing_timestamp": datetime.now(timezone.utc).isoformat()
    }

    extracted_sections = []
    subsection_analysis = []
    rank = 1

    for doc in data["documents"]:
        filename = doc["filename"]
        pdf_path = os.path.join(pdf_dir, filename)

        if not os.path.exists(pdf_path):
            print(f"[WARNING] File not found: {filename}")
            continue

        pages = extract_text_from_pdf(pdf_path)
        if not pages:
            print(f"[WARNING] No readable text in: {filename}")
            continue

        for page_number, full_text in pages[:MAX_PAGES]:
            if not full_text.strip():
                continue

            section_title = full_text.split("\n")[0][:100].strip()
            snippet = full_text.strip()[:500]
            keywords = extract_keywords(snippet)
            suggested_day = assign_day_rank(rank)

            extracted_sections.append({
                "document": filename,
                "section_title": section_title,
                "importance_rank": rank,
                "page_number": page_number,
                "suggested_day": suggested_day,
                "keywords": keywords
            })

            subsection_analysis.append({
                "document": filename,
                "section_title": section_title,
                "refined_text": snippet,
                "page_number": page_number
            })

            rank += 1

    result = {
        "metadata": metadata,
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"[SUCCESS] Processed: {collection_path} → {output_path}")

# Process all Collection folders
def process_all_collections():
    for name in os.listdir(BASE_DIR):
        path = os.path.join(BASE_DIR, name)
        if os.path.isdir(path) and name.lower().startswith("collection"):
            process_collection(path)

if __name__ == "__main__":
    process_all_collections()
