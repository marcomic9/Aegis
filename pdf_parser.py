import fitz  # PyMuPDF
import re
from typing import List, Dict

class PDFParser:
    def extract_data(self, pdf_path: str) -> List[Dict[str, str]]:
        raise NotImplementedError("Subclasses must implement extract_data")

class LightstonePDFParser(PDFParser):
    def extract_data(self, pdf_path: str) -> List[Dict[str, str]]:
        try:
            doc = fitz.open(pdf_path)
            results = []

            # Flexible pattern for: unit (digits), size (digits), name (words), identifier (digits, usually 13)
            # Adjust if your identifier length differs
            pattern = re.compile(
                r"(\d+)\s+(\d+)\s+([A-Z\s]+?)\s+(\d{13})"
            )

            print("=== SAMPLE TEXT BLOCKS FROM PDF ===")
            for page in doc:
                blocks = page.get_text("blocks")
                for i, block in enumerate(blocks[:5]):  # just show first 5 blocks per page for quick check
                    text = block[4].strip()
                    print(f"Block {i+1}:\n{text}\n---")

                # Now extract matches from all blocks
                for block in blocks:
                    text = block[4].strip()
                    matches = pattern.findall(text)
                    for match in matches:
                        unit, size, name, identifier = match
                        results.append({
                            "unit": unit,
                            "size": size,
                            "name": name.strip(),
                            "identifier": identifier
                        })

            doc.close()

            if not results:
                raise ValueError("No matching data found in PDF.")

            return results

        except FileNotFoundError:
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")

def extract_data_from_pdf(pdf_path: str, format_type: str = "lightstone") -> List[Dict[str, str]]:
    parsers: Dict[str, PDFParser] = {
        "lightstone": LightstonePDFParser()
    }

    parser = parsers.get(format_type.lower())
    if not parser:
        raise ValueError(f"Unsupported PDF format: {format_type}")

    return parser.extract_data(pdf_path)

def main():
    try:
        pdf_path = "Owners in Flame manor.pdf"  # Change to your PDF file path
        data = extract_data_from_pdf(pdf_path, format_type="lightstone")
        print("\n=== EXTRACTED DATA ===")
        for entry in data:
            print(entry)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
