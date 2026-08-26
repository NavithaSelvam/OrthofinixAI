import cv2
import numpy as np
import io
from PIL import Image, ImageDraw

def generate_test_image_A():
    # Symmetric, well-aligned dental arch
    img = Image.new("RGB", (640, 480), color=(180, 70, 80)) # gingival background
    draw = ImageDraw.Draw(img)
    # Draw upper teeth (white rounded rectangles)
    teeth_x = [120, 160, 200, 240, 280, 320, 360, 400, 440, 480, 520]
    for x in teeth_x:
        draw.rounded_rectangle([x - 16, 160, x + 16, 230], radius=5, fill=(245, 245, 235), outline=(150, 150, 150))
    # Draw lower teeth
    teeth_lower_x = [140, 180, 220, 260, 300, 340, 380, 420, 460, 500]
    for x in teeth_lower_x:
        draw.rounded_rectangle([x - 14, 245, x + 14, 310], radius=5, fill=(240, 240, 230), outline=(150, 150, 150))
    return np.array(img)

def generate_test_image_B():
    # Asymmetric, severely crowded dental arch with staggered teeth and midline shift
    img = Image.new("RGB", (640, 480), color=(140, 60, 70))
    draw = ImageDraw.Draw(img)
    # Draw upper teeth with irregular spacing and tilted/staggered Y
    teeth_x = [110, 155, 185, 230, 290, 360, 395, 450, 485, 530]
    teeth_y = [170, 150, 180, 145, 175, 155, 185, 160, 170, 155]
    for x, y in zip(teeth_x, teeth_y):
        draw.rounded_rectangle([x - 18, y, x + 18, y + 75], radius=7, fill=(235, 230, 220), outline=(100, 100, 100))
    # Draw lower teeth shifted to the right (severe midline deviation)
    teeth_lower_x = [160, 205, 245, 295, 335, 385, 435, 475, 520]
    teeth_lower_y = [260, 245, 270, 250, 265, 245, 260, 250, 265]
    for x, y in zip(teeth_lower_x, teeth_lower_y):
        draw.rounded_rectangle([x - 15, y, x + 15, y + 65], radius=5, fill=(230, 230, 215), outline=(100, 100, 100))
    return np.array(img)

imgA = generate_test_image_A()
imgB = generate_test_image_B()
print(f"Generated Image A shape: {imgA.shape}, Image B shape: {imgB.shape}")
