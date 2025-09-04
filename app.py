from ui import SnipOverlay, show_result_window
from ocr import ocr_image_to_text
from parse import extract_numbers_and_total

def on_region_captured(pil_image):
    # 1) OCR
    text = ocr_image_to_text(pil_image)
    # 2) Parse & total
    total, items = extract_numbers_and_total(text)
    # 3) Show result window
    show_result_window(total, items, original_image=pil_image, raw_text=text)

if __name__ == "__main__":
    # Launch the snip overlay; it will call on_region_captured(image) on mouse release
    SnipOverlay(on_region_captured).run()
