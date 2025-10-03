#!/usr/bin/env python3
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont
import time

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32  # Adjust to your panel height
options.cols = 64  # Adjust to your panel width
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
options.brightness = 70

matrix = RGBMatrix(options=options)

# Load font using PIL (same as your train app)
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
except:
    font = ImageFont.load_default()

# Your message
message = "Happy Birthday! Love you!"

# Get text dimensions
dummy_image = Image.new('RGB', (1, 1))
dummy_draw = ImageDraw.Draw(dummy_image)
text_bbox = dummy_draw.textbbox((0, 0), message, font=font)
text_width = text_bbox[2] - text_bbox[0]
text_height = text_bbox[3] - text_bbox[1]

# Starting position (start off-screen to the right)
pos = matrix.width

try:
    while True:
        # Create image for this frame
        image = Image.new('RGB', (matrix.width, matrix.height))
        draw = ImageDraw.Draw(image)
        
        # Draw text at current position
        # Pink color (255, 0, 128)
        draw.text((pos, (matrix.height - text_height) // 2), message, font=font, fill=(255, 0, 128))
        
        # Display on matrix
        matrix.SetImage(image)
        
        # Move text to the left
        pos -= 1
        
        # Reset position when text has scrolled completely off screen
        if pos + text_width < 0:
            pos = matrix.width
        
        # Control scroll speed (lower = faster)
        time.sleep(0.03)

except KeyboardInterrupt:
    matrix.Clear()