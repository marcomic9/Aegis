# excel_writer.py
"""
Handles writing results to an Excel file using openpyxl.
Exports: write_results_to_excel(results: Dict[str, List[str]], output_path: str)
"""
from typing import Dict, List
from openpyxl import Workbook

def write_results_to_excel(results: Dict[str, List[str]], output_path: str):
    wb = Workbook()
    ws = wb.active
    ws.title = "Results"
    ws.append(["ID", "Cell 1", "Cell 2", "Cell 3"])
    for id_value, numbers in results.items():
        row = [id_value] + numbers + [""] * (3 - len(numbers))
        ws.append(row)
    wb.save(output_path)
