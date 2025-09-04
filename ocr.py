from PIL import Image, ImageOps
import pytesseract

# If Tesseract isn't on PATH (Windows), set it explicitly:
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

WHITELIST = "0123456789.,-()$€£₹% RsPKR"

def _preprocess(img):
    # Light preprocessing: grayscale + autocontrast; keep simple for beginners
    g = ImageOps.grayscale(img)
    g = ImageOps.autocontrast(g)
    return g

def ocr_image_to_text(pil_image):
    proc = _preprocess(pil_image)
    # PSM 6 = assume a block of text, good for tables
    config = f'--psm 6 -c tessedit_char_whitelist="{WHITELIST}"'
    text = pytesseract.image_to_string(proc, config=config)
    return text
