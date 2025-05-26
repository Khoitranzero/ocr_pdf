import pdfplumber
import fitz  # PyMuPDF
import pytesseract
import PyPDF2
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO
import io
import numpy as np
import cv2
from pyvi import ViTokenizer, ViUtils
import easyocr

# Cấu hình Tesseract
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"



# hàm lấy văn bản từ file pdf
# Dùng pdfplumber để open và lấy dữ liệu từ file pdf (lấy dữ liệu theo trang)
def extract_text_from_pdf(pdf_path):
    output = {}
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and text.strip():
                output[f"page_{i+1}"] = text.strip()
    return output

# hàm kiểm tra xem cấu trúc văn bản có phải là table hay không(nếu không đủ 2 colum hay có nhiều ô trống)
def is_probably_table(table, min_cols=2, max_empty_ratio=0.5):
    if not table or len(table) == 0:
        return False


    num_cols = len(table[0])
    if num_cols < min_cols:
        return False

    total_cells = sum(len(row) for row in table)
    empty_cells = sum(cell is None or str(cell).strip() == "" for row in table for cell in row)
    empty_ratio = empty_cells / total_cells if total_cells > 0 else 1

    return empty_ratio < max_empty_ratio
# hàm lấy dữ liệu từ table trong file pdf
# Dùng pdfplumber để open và lấy dữ liệu từ table trong file pdf (lấy dữ liệu theo trang)
def extract_tables_from_pdf(pdf_path):
    tables_output = {}
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            raw_tables = page.extract_tables()
            valid_tables = []

            for table in raw_tables:
                if is_probably_table(table):
                    valid_tables.append(table)

            if valid_tables:
                tables_output[f"page_{i+1}"] = valid_tables
    return tables_output


# lấy dữ liệu hình ảnh trong file pdf. 
# hàm xoay ảnh, nếu ocr ra kết quả mỗi dòng có khoảng 1-2 ký tự=> cần xoay ảnh
def is_likely_rotated(text_lines, threshold=0.6):
    short_lines = [line for line in text_lines if len(line.strip()) <= 2]
    if not text_lines:
        return False
    ratio = len(short_lines) / len(text_lines)
    return ratio >= threshold  # nếu > 60% dòng ngắn → bị xoay
# hàm lấy ocr hình ảnh 
# dùng fitz  # PyMuPDF để mở file pdf và xác định và trích xuất phần hình ảnh có trong file pdf
# dùng công cụ easyocr để ocr ảnh để lấy nội dung
# nếu ocr ra kết quả mỗi dòng có khoảng 1-2 ký tự=> cần xoay ảnh

def save_and_easyocr(pdf_path, save_images=True):
    doc = fitz.open(pdf_path)
    all_text = []
    reader = easyocr.Reader(['vi', 'en'])

    for page_number, page in enumerate(doc, start=1):
  
        images = page.get_images(full=True)
        if not images:
            continue

        for img_index, img in enumerate(images, start=1):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

            # if save_images:
            #     pil_image.save(f"page{page_number}_img{img_index}_original.png") # lưu ảnh để kiểm tra

            # Chuyển ảnh sang numpy
            img_np = np.array(pil_image)

            # OCR thử lần đầu
            result = reader.readtext(img_np, detail=0)
            text_lines = result if isinstance(result, list) else []
            text_values = [line.strip() for line in text_lines if isinstance(line, str)]

            # Kiểm tra xem ảnh có thể bị xoay không
            if is_likely_rotated(text_values):
                pil_image = pil_image.rotate(270, expand=True)
                img_np = np.array(pil_image)
                result = reader.readtext(img_np, detail=0)
                text_values = [line.strip() for line in result if isinstance(line, str)]

            final_text = '\n'.join(text_values)
            all_text.append(f"[Trang {page_number} - Hình {img_index}]\n{final_text.strip()}")

    doc.close()
    return "\n\n".join(all_text)

