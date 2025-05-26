import os
import uuid
import json
from datetime import datetime
import def_pdf

def get_file_metadata(file_path):
    file_stats = os.stat(file_path)
    file_name = os.path.basename(file_path)
    file_size = file_stats.st_size
    created_at = datetime.now().isoformat()
    updated_at = datetime.fromtimestamp(file_stats.st_mtime).isoformat()

    return file_name, file_size, created_at, updated_at

if __name__ == "__main__":
    pdf_path = "../PDF/sample/250521.MEG/3. HỒ SƠ TKKT/THUYET MINH/MEG. CP. THUYET MINH TKKT 1 rev signed.pdf"
    pdf_path = "../PDF/sample/output.pdf"
    # pdf_path = "../PDF/sample/MEG. CP. THUYET MINH TKKT 1 rev signed-trang-1.pdf"
    text_data = def_pdf.extract_text_from_pdf(pdf_path)
    table_data = def_pdf.extract_tables_from_pdf(pdf_path)
    # text_data = {}
    # table_data = {}
    # ocr_data = {}
    ocr_data = def_pdf.save_and_easyocr(pdf_path)

     # Lấy thông tin file
    file_name, file_size, created_at, updated_at = get_file_metadata(pdf_path)


    result = {
        "id": str(uuid.uuid4()),
        "name": file_name,
        "data": {
            "text": text_data,
            "table": table_data,
            "image": ocr_data
        },
        "created_at": created_at,
        "updated_at": updated_at,
        "file_size": file_size
    }
#lưu kết quả vào file json
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
