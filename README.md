# 📘 Adobe India Hackathon 2025 — Round 1A
## Challenge: 🧩 Connecting the Dots Through Docs

---

### 💡 Overview

This project implements a PDF outline extractor as required in **Round 1A** of Adobe’s India Hackathon 2025. The objective is to process PDF documents and generate a structured JSON file containing:

- The **Document Title**
- A hierarchical **Outline** of Headings (`H1`, `H2`, `H3`)
- Page numbers and structure based on visual and semantic cues

---

### ✅ What the Solution Does

- Accepts one or more PDFs (max 50 pages) via the `/app/input` directory (or the provided `sample_dataset/pdfs`)
- Automatically extracts:
  - Title
  - Headings with level (`H1`, `H2`, `H3`)
  - Corresponding page numbers
- Produces clean, valid JSON outputs in `/app/output/` (or `sample_dataset/outputs`)
- Follows Adobe’s provided schema (`sample_dataset/schema/output_schema.json`)

---

### 🧠 Approach

#### 1. Text Block Extraction
- Uses PyMuPDF (`fitz`) to extract font size, style, position (y-coordinates), and text.

#### 2. Title Detection
- Finds the largest font block on the **first page** and assigns it as the document title.

#### 3. Heading Classification
- Applies visual and semantic heuristics:
  - Larger-than-body font sizes
  - Bold text
  - Numbering patterns (e.g. `1.2.3`, `A.`)
  - UPPERCASE short spans
- Dynamically maps top 3 font sizes to `H1`, `H2`, `H3`.

#### 4. Output Generation
- Results are saved as structured JSON, aligned with the official schema.

---

### 📁 Project Structure

```
Adobe-Round-1A/
├── process_pdfs.py                # Main logic script
├── Dockerfile                     # Container definition
├── requirements.txt               # Python dependencies
├── sample_dataset/
│   ├── pdfs/                      # Input sample PDFs
│   ├── outputs/                   # Output JSONs will be saved here
│   └── schema/output_schema.json  # JSON output format
└── .gitignore                     # Config/system files
```

---

### ▶️ How to Run

#### 🧪 Local Testing

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the processor:

```bash
python process_pdfs.py
```

> Outputs will appear in `sample_dataset/outputs/`

---

#### 🐳 Docker Build & Run (as per the given requirement)

```bash
# Build (for amd64 CPU)
docker build --platform linux/amd64 -t adobe_round1a:submission .

# Run (automatically processes all PDFs in input/)
docker run --rm \
  -v $(pwd)/sample_dataset/pdfs:/app/input \
  -v $(pwd)/sample_dataset/outputs:/app/output \
  --network none \
  adobe_round1a:submission
```

---

### 📌 Requirements

- **CPU-only** environment (no GPU)
- **No network access**
- **≤ 10s runtime** for 50-page PDFs
- **≤ 200MB model size** (our solution uses no ML models)
- Compatible with **linux/amd64**

---

### 🧪 Output Example (from schema)

```json
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "1. Introduction", "page": 1 },
    { "level": "H2", "text": "1.1 Background", "page": 2 },
    { "level": "H3", "text": "1.1.1 History", "page": 3 }
  ]
}
```

---

### 🔄 Ready for Round 1B

This outline structure serves as a foundation for Round 1B’s persona-driven section extraction. Grouping and importance ranking logic can be layered on top of the extracted structure.

---

### 👨‍💻 About our team

Team Name-: Coooders
Member Names-: 
1. Mehul Gupta
2. Awanee
3. Divjot Singh Gulati
