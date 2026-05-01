# Extract raw text from a PDF screenplay file
# Use pdfplumber to read PDF and extract text page by page
# Preserve page numbers during extraction
# Pass extracted text to text_parser.py for scene parsing

import pdfplumber
import re
def extract_text_from_pdf(file_path: str) -> list[tuple[int, str]]:
    # Returns list of (page_number, text) tuples instead of single string
    # This preserves page numbers for scene assignment downstream
    pages = []

    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text(layout=True)
            if text:
                # remove standalone page numbers like "2.", "15."
                text = "\n".join(
                    line for line in text.splitlines()
                    if not re.match(r"^\d+\.?$", line.strip())
                )
                pages.append((i, text))

    return pages

if __name__ == "__main__":
    import sys
    import os

    if len(sys.argv) < 2:
        print("Usage: python parser/pdf_parser.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    pages = extract_text_from_pdf(pdf_path)

    # save next to input as .txt
    out_path = os.path.splitext(pdf_path)[0] + "_extracted.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        for page_number, text in pages:
            f.write(text + "\n")

    print(f"Saved extracted text to: {out_path}")
    print("\nPreview:\n")
    for page_number, text in pages[:2]:
        print(f"--- Page {page_number} ---")
        print(text[:500])

