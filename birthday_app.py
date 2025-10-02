#!/usr/bin/env python3
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32  # Adjust to your panel height
options.cols = 64  # Adjust to your panel width
options.chain_length = 1  # If you have multiple panels chained
options.parallel = 1
options.hardware_mapping = 'adafruit_hat'  # or 'adafruit-hat' depending on your setup
options.brightness = 70  # Adjust brightness (0-100)

matrix = RGBMatrix(options=options)

# Load font
font = graphics.Font()
font.LoadFont("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")  # Adjust path if needed
# Or use the built-in fonts:
# font.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/7x13.bdf")

# Set text color (RGB)
text_color = graphics.Color(255, 0, 128)  # Pink color

# Your message
message = "Happy Birthday! ❤️ Love you!"

# Create offscreen canvas
offscreen_canvas = matrix.CreateFrameCanvas()

# Get text width
text_width = len(message) * 7  # Approximate, adjust based on your font

# Starting position (start off-screen to the right)
pos = offscreen_canvas.width

try:
    while True:
        offscreen_canvas.Clear()
        
        # Draw text at current position
        graphics.DrawText(offscreen_canvas, font, pos, 20, text_color, message)
        
        # Move text to the left
        pos -= 1
        
        # Reset position when text has scrolled completely off screen
        if pos + text_width < 0:
            pos = offscreen_canvas.width
        
        # Swap canvas
        offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
        
        # Control scroll speed (lower = faster)
        time.sleep(0.03)

except KeyboardInterrupt:
    matrix.Clear()