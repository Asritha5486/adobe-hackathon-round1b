import os
import json
import fitz  # PyMuPDF
from datetime import datetime, timezone


BASE_DIR = '.'
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text_by_page = []
    for i, page in enumerate(doc):
        text_by_page.append((i + 1, page.get_text()))
    return text_by_page

def process_collection(collection_path):
    input_path = os.path.join(collection_path, "challenge1b_input.json")
    output_path = os.path.join(collection_path, "challenge1b_output.json")
    pdf_dir = os.path.join(collection_path, "PDFs")

    with open(input_path, "r") as f:
        data = json.load(f)

    metadata = {
        "input_documents": [d["filename"] for d in data["documents"]],
        "persona": data["persona"]["role"],
        "job_to_be_done": data["job_to_be_done"]["task"],
        "processing_timestamp": datetime.now(timezone.utc).isoformat()

    }

    extracted_sections = []
    subsection_analysis = []

    for doc in data["documents"]:
        filename = doc["filename"]
        pdf_path = os.path.join(pdf_dir, filename)
        if not os.path.exists(pdf_path):
            continue

        pages = extract_text_from_pdf(pdf_path)

        for page_number, text in pages[:3]:  # Analyze first 3 pages as example
            section = {
            "document": filename,
            "section_title": text.strip().split('\n')[0][:100],  # Use first line or heading-like content
            "importance_rank": page_number,
            "page_number": page_number,
            "extracted_text": text.strip()[:500]  # Optional: give a snippet for context
            }

            extracted_sections.append(section)

            subsection = {
                "document": filename,
                "refined_text": text.strip()[:500],  # Truncated
                "page_number": page_number
            }
            subsection_analysis.append(subsection)

    result = {
        "metadata": metadata,
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)


    print(f" Processed {collection_path}")

def process_all_collections():
    for name in os.listdir(BASE_DIR):
        path = os.path.join(BASE_DIR, name)
        if os.path.isdir(path) and name.lower().startswith("collection"):
            process_collection(path)

if __name__ == "__main__":
    process_all_collections()
