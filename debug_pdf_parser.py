# debug_pdf_parser.py
import fitz
import re

def debug_extract_ids(pdf_path: str):
    try:
        doc = fitz.open(pdf_path)
        identifier_x_range = None
        identifier_found = False
        ids = []

        for page_num, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            print(f"\n--- Page {page_num + 1} ---")

            for block in blocks:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        x0 = span["bbox"][0]
                        x1 = span["bbox"][2]

                        if not identifier_found and "IDENTIFIER" in text.upper():
                            identifier_x_range = (x0 - 5, x1 + 5)
                            identifier_found = True
                            print(f"Found IDENTIFIER at x-range: {identifier_x_range}")
                            continue

                        print(f"Text: '{text}' | x0: {x0:.2f} | x1: {x1:.2f}")

                        if identifier_found and re.match(r"^\d{9}$", text):
                            if identifier_x_range and identifier_x_range[0] <= x0 <= identifier_x_range[1]:
                                print(f">>> Matched ID in range: {text}")
                                ids.append(text)
                            else:
                                print(f">>> Skipped (outside range): {text}")

        doc.close()
        if ids:
            print("\n✅ Extracted IDs:", ids)
        else:
            print("\n⚠️ No IDs extracted.")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    debug_extract_ids("Owners in Flame manor.pdf")
