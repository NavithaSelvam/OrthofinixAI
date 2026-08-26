import cv2
import os

def debug_image():
    image_path = "uploads/5b91d2b0-03bb-40df-b235-6cfc9e5b1f47.jpg"
    if not os.path.exists(image_path):
        return
        
    img = cv2.imread(image_path)
    if img is None:
        return
        
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    min_area = (h * w) * 0.001
    max_area = (h * w) * 0.1
    print(f"Area limits: min={min_area:.1f}, max={max_area:.1f}")
    
    areas = [cv2.contourArea(c) for c in contours]
    areas.sort(reverse=True)
    print("Top 15 contour areas:", areas[:15])

if __name__ == "__main__":
    debug_image()
