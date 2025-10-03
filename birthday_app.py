#!/usr/bin/env python3
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont
import time

# Configuration for the matrix (matching your working demo)
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
options.gpio_slowdown = 3
options.brightness = 70

matrix = RGBMatrix(options=options)

# Load font using PIL
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
except:
    font = ImageFont.load_default()

# Message parts with different colors
message_parts = [
    ("Happy   ", (255, 0, 128)),    # Pink
    ("30", (255, 215, 0)),        # Gold
    ("th!!", (0, 191, 255))         # Sky blue
]

# Calculate total text width
dummy_image = Image.new('RGB', (1, 1))
dummy_draw = ImageDraw.Draw(dummy_image)
total_width = 0
for text, _ in message_parts:
    bbox = dummy_draw.textbbox((0, 0), text, font=font)
    total_width += bbox[2] - bbox[0]

# Starting position
pos = matrix.width

try:
    while True:
        # Create image for this frame
        image = Image.new('RGB', (matrix.width, matrix.height))
        draw = ImageDraw.Draw(image)
        
        # Draw each part of the message with its color
        current_x = pos
        for text, color in message_parts:
            draw.text((current_x, 9), text, font=font, fill=color)
            bbox = draw.textbbox((0, 0), text, font=font)
            current_x += bbox[2] - bbox[0]
        
        # Display on matrix
        matrix.SetImage(image)
        
        # Move text to the left
        pos -= 1
        
        # Reset position when text has scrolled completely off screen
        if pos + total_width < 0:
            pos = matrix.width
        
        # Control scroll speed
        time.sleep(0.03)

except KeyboardInterrupt:
    matrix.Clear()