import os
import json
import fitz  # PyMuPDF
from datetime import datetime, timezone

# Settings
MAX_PAGES = 3
BASE_DIR = '.'

# Keywords for context-based scoring
KEYWORDS_BY_PERSONA = {
    "Travel Planner": ["city", "cities", "hotel", "stay", "restaurant", "attraction", "activity", "culture", "tip"],
    "HR Professional": ["policy", "leave", "vacation", "hr", "regulation", "entitlement", "benefit"],
    "Food Contractor": ["vegetarian", "gluten", "buffet", "recipe", "menu", "dinner", "sides", "ingredients"]
}

GENERIC_HEADERS = {"introduction", "overview", "summary", "conclusion"}

# Scoring-based rank
def calculate_relevance(text, persona):
    if persona not in KEYWORDS_BY_PERSONA:
        return 0
    keywords = KEYWORDS_BY_PERSONA[persona]
    score = sum(text.lower().count(k) for k in keywords)
    return score

# Assign day using topic keywords
def assign_day_by_topic(text):
    lower = text.lower()
    if any(k in lower for k in ["city", "cities", "marseille", "nice"]):
        return 1
    elif any(k in lower for k in ["restaurant", "hotel", "food", "dish", "cuisine"]):
        return 2
    elif any(k in lower for k in ["activity", "thing", "do", "museum", "beach"]):
        return 3
    elif any(k in lower for k in ["tip", "pack", "travel", "culture", "language"]):
        return 4
    return 0

def extract_keywords(text):
    words = [word.lower() for word in text.split() if len(word) > 4 and word.isalpha()]
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    return [w for w, _ in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]]

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        return [(i + 1, page.get_text().strip()) for i, page in enumerate(doc)]
    except Exception as e:
        print(f"[ERROR] Failed to process {pdf_path}: {e}")
        return []

def clean_title(raw_title):
    first_line = raw_title.split('\n')[0].strip()
    if first_line.lower() in GENERIC_HEADERS or len(first_line) < 5:
        return None
    return first_line[:100]

def process_collection(collection_path):
    input_path = os.path.join(collection_path, "challenge1b_input.json")
    output_path = os.path.join(collection_path, "challenge1b_output.json")
    pdf_dir = os.path.join(collection_path, "PDFs")

    if not os.path.exists(input_path):
        print(f"[SKIP] No input JSON found in {collection_path}")
        return

    with open(input_path, "r") as f:
        data = json.load(f)

    persona = data["persona"]["role"]
    task = data["job_to_be_done"]["task"]

    metadata = {
        "input_documents": [doc["filename"] for doc in data["documents"]],
        "persona": persona,
        "job_to_be_done": task,
        "processing_timestamp": datetime.now(timezone.utc).isoformat()
    }

    extracted_sections = []
    subsection_analysis = []
    temp_sections = []

    for doc in data["documents"]:
        filename = doc["filename"]
        pdf_path = os.path.join(pdf_dir, filename)

        if not os.path.exists(pdf_path):
            print(f"[WARNING] File not found: {filename}")
            continue

        pages = extract_text_from_pdf(pdf_path)
        for page_number, full_text in pages[:MAX_PAGES]:
            if not full_text.strip():
                continue

            title = clean_title(full_text)
            if not title:
                continue

            snippet = full_text[:500]
            keywords = extract_keywords(snippet)
            relevance_score = calculate_relevance(full_text, persona)
            suggested_day = assign_day_by_topic(full_text)

            temp_sections.append({
                "document": filename,
                "section_title": title,
                "relevance_score": relevance_score,
                "page_number": page_number,
                "refined_text": snippet,
                "keywords": keywords,
                "suggested_day": suggested_day
            })

    # Rank based on relevance score
    sorted_sections = sorted(temp_sections, key=lambda x: -x["relevance_score"])
    for i, sec in enumerate(sorted_sections):
        extracted_sections.append({
            "document": sec["document"],
            "section_title": sec["section_title"],
            "importance_rank": i + 1,
            "page_number": sec["page_number"],
            "suggested_day": sec["suggested_day"],
            "keywords": sec["keywords"]
        })
        subsection_analysis.append({
            "document": sec["document"],
            "section_title": sec["section_title"],
            "refined_text": sec["refined_text"],
            "page_number": sec["page_number"]
        })

    output = {
        "metadata": metadata,
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"[SUCCESS] Processed: {collection_path} → {output_path}")

def process_all_collections():
    for name in os.listdir(BASE_DIR):
        path = os.path.join(BASE_DIR, name)
        if os.path.isdir(path) and name.lower().startswith("collection"):
            process_collection(path)

if __name__ == "__main__":
    process_all_collections()