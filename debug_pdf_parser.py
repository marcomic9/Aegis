# debug_pdf_parser.py
import fitz
import re
import db

def debug_extract_owners(pdf_path: str):
    try:
        doc = fitz.open(pdf_path)
        results = []
        # Pattern: unit (digits), size (digits), name (words + spaces), identifier (13 digits)
        pattern = re.compile(r"(\d+)\s+(\d+)\s+([A-Z\s]+?)\s+(\d{13})")
        pdf_filename = pdf_path
        for page_num, page in enumerate(doc):
            print(f"\n--- Page {page_num + 1} ---")
            blocks = page.get_text("blocks")
            for block in blocks:
                text = block[4].strip()
                print(f"[BLOCK TEXT]\n{text}\n---")
                matches = pattern.findall(text)
                for match in matches:
                    unit, size, name, identifier = match
                    print(f"[MATCH] unit: {unit}, size: {size}, name: {name.strip()}, identifier: {identifier}")
                    record = {
                        "unit": unit,
                        "size": size,
                        "name": name.strip(),
                        "identifier": identifier
                    }
                    results.append(record)
                    # Save to DB (other fields left blank for demo)
                    db.insert_record(
                        pdf_filename=pdf_filename,
                        municipality="",
                        township="",
                        sectional_scheme_name="",
                        unit=unit,
                        size=size,
                        name=name.strip(),
                        identifier=identifier
                    )
                    print(f"[DB] Saved record for identifier: {identifier}")
        doc.close()
        if results:
            print(f"\n✅ Extracted and saved {len(results)} owner records.")
        else:
            print("\n⚠️ No owner records extracted.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    debug_extract_owners("Owners in Flame manor.pdf")
