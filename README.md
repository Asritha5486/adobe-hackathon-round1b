# Challenge 1B — PDF Collection Processing

This project is part of the Adobe India Hackathon 2025 — Connecting the Dots Challenge.

---

## Folder Structure

```
Challenge_1b/
├── Collection 1/
│   ├── PDFs/
│   ├── challenge1b_input.json
│   └── challenge1b_output.json  (generated output)
├── Collection 2/
│   ├── PDFs/
│   ├── challenge1b_input.json
│   └── challenge1b_output.json
├── Collection 3/
│   ├── PDFs/
│   ├── challenge1b_input.json
│   └── challenge1b_output.json
├── process_collections.py   (main processing script)
└── README.md                (this file)
```

---

## Requirements

- Python 3.7 or higher  
- PyMuPDF (install via `pip install pymupdf`)

---

## How to Run

1. Open terminal/command prompt.

2. Navigate to the `Challenge_1b` directory:

   ```bash
   cd path/to/Challenge_1b
   ```

3. Install dependencies if needed:

   ```bash
   pip install pymupdf
   ```

4. Run the processing script:

   ```bash
   python process_collections.py
   ```

5. The script will process all collections folders (`Collection 1`, `Collection 2`, `Collection 3`), read PDFs and input JSONs, and generate/update `challenge1b_output.json` files in each collection folder.

---

## Optional: Run with Docker

If you want to use Docker (Dockerfile not required by the challenge but included optionally):

1. Build the Docker image:

   ```bash
   docker build -t pdfprocessor .
   ```

2. Run the container with current folder mounted:

   ```bash
   docker run --rm -v "$(pwd):/app" pdfprocessor
   ```

Outputs will be saved in the mounted folders.

---

## Notes

- The script extracts text from the first 3 pages of each PDF to create structured outputs.  
- Outputs include metadata (persona, job), extracted sections with titles and text snippets.  
- Running the script multiple times will overwrite previous output JSON files.

---

## Contact

For questions or clarifications, please contact:Asritha Chunduri/chasritha33@gmail.com
---

Good luck with your submission! 
