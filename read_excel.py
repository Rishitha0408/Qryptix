import openpyxl
import json
import sys

def read_excel(file_path):
    try:
        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active
        data = []
        headers = [cell.value for cell in sheet[1]]
        
        for row in sheet.iter_rows(min_row=2, values_only=True):
            data.append(dict(zip(headers, row)))
        
        return data
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    file_path = "dummy_doctors_updated (2).xlsx"
    content = read_excel(file_path)
    if isinstance(content, list) and len(content) > 0:
        print("Keys:", list(content[0].keys()))
        print("First 5 records:")
        print(json.dumps(content[:5], indent=2))
    else:
        print(content)
