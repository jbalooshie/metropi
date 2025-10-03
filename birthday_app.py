#!/usr/bin/env python3
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont
import time

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32  # Change this to match your panel
options.cols = 64  # Change this to match your panel
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'  # Try 'adafruit-hat', 'adafruit-hat-pwm', or 'regular'
options.brightness = 70
options.gpio_slowdown = 4  # Try values between 1-4 if you see flickering/distortion
options.disable_hardware_pulsing = True  # Can help with some displays

matrix = RGBMatrix(options=options)

# Load font using PIL
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
except:
    font = ImageFont.load_default()

# Your message
message = "Happy Birthday! Love you!"

# Starting position
pos = matrix.width

try:
    while True:
        # Create image for this frame
        image = Image.new('RGB', (matrix.width, matrix.height))
        draw = ImageDraw.Draw(image)
        
        # Draw text - simple white color first to test
        draw.text((pos, 10), message, font=font, fill=(255, 255, 255))
        
        # Display on matrix
        matrix.SetImage(image)
        
        # Move text to the left
        pos -= 2
        
        # Reset position
        if pos < -200:  # Adjust based on message length
            pos = matrix.width
        
        # Control scroll speed
        time.sleep(0.05)

except KeyboardInterrupt:
    matrix.Clear()