import cv2
import numpy as np
import os

def check():
    path = "uploads/5b91d2b0-03bb-40df-b235-6cfc9e5b1f47.jpg"
    if not os.path.exists(path):
        return
    img = cv2.imread(path)
    if img is None:
        print("Failed to read")
        return
    print("Mean color:", img.mean(axis=(0, 1)))
    print("Min/Max:", img.min(), img.max())
    print("Shape:", img.shape)
    
if __name__ == "__main__":
    check()
