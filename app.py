import requests
import time
from typing import List, Dict
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont
import configparser
import os
from datetime import datetime, time as dt_time

def load_config() -> dict:
    """
    Load configuration from config.ini file.
    
    Returns:
        dict: Configuration settings
    """
    config = configparser.ConfigParser()
    
    # Check if config file exists
    if not os.path.exists('config.ini'):
        # Create default config file
        config['WMATA'] = {
            'api_key': 'your-api-key-here',
            'station_codes': 'A01',
            'update_interval': '30'
        }
        
        config['MATRIX'] = {
            'rows': '32',
            'cols': '64',
            'chain_length': '1',
            'parallel': '1',
            'hardware_mapping': 'regular',
            'gpio_slowdown': '2'
        }
        
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
            print("Created default config.ini file. Please edit with your settings.")
            exit(1)
            
    config.read('config.ini')
    return config

def get_train_predictions(station_codes: str, api_key: str) -> List[Dict]:
    """
    Get train predictions for specified station codes from WMATA API.
    
    Args:
        station_codes (str): Comma-separated list of station codes
        api_key (str): WMATA API key
        
    Returns:
        List[Dict]: List of dictionaries containing next 3 trains' information
    """
    url = f"http://api.wmata.com/StationPrediction.svc/json/GetPrediction/{station_codes}"
    headers = {"api_key": api_key}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        trains = data.get("Trains", [])[:3]
        
        train_info = [
            {
                "Car": train["Car"],
                "Destination": train["Destination"],
                "Line": train["Line"],
                "Min": train["Min"]
            }
            for train in trains
        ]
        return train_info
        
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return []
    except (KeyError, ValueError) as e:
        print(f"Error parsing response data: {e}")
        return []

def get_line_color(line: str) -> tuple:
    """Return RGB color tuple for each Metro line."""
    colors = {
        "RD": (255, 0, 0),    # Red
        "BL": (0, 0, 255),    # Blue
        "YL": (255, 255, 0),  # Yellow
        "OR": (255, 165, 0),  # Orange
        "GR": (0, 255, 0),    # Green
        "SV": (192, 192, 192) # Silver
    }
    return colors.get(line, (255, 255, 255))  # Default to white if line not found

class LEDMatrixDisplay:
    def __init__(self, matrix_config: configparser.SectionProxy):
        # Configuration for the matrix
        options = RGBMatrixOptions()
        options.rows = int(matrix_config.get('rows', 32))
        options.cols = int(matrix_config.get('cols', 64))
        options.chain_length = int(matrix_config.get('chain_length', 1))
        options.parallel = int(matrix_config.get('parallel', 1))
        options.hardware_mapping = matrix_config.get('hardware_mapping', 'regular')
        options.gpio_slowdown = int(matrix_config.get('gpio_slowdown', 2))
        
        # Create matrix instance
        self.matrix = RGBMatrix(options=options)
        
        # Set initial brightness
        self.update_brightness()
        
        # Create a blank image for drawing
        self.image = Image.new('RGB', (self.matrix.width, self.matrix.height))
        self.draw = ImageDraw.Draw(self.image)
        
        # Try to load a font
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 8)
        except:
            self.font = ImageFont.load_default()

    def is_night_time(self) -> bool:
        """Check if current time is between 10 PM and 5 AM"""
        current_time = datetime.now().time()
        night_start = dt_time(22, 0)  # 10 PM
        night_end = dt_time(5, 0)    # 5 AM
        
        if night_start <= night_end:
            return night_start <= current_time <= night_end
        else:  # Handle case when period spans midnight
            return current_time >= night_start or current_time <= night_end

    def update_brightness(self):
        """Update the matrix brightness based on time of day"""
        if self.is_night_time():
            self.matrix.brightness = 50  # 50% brightness
        else:
            self.matrix.brightness = 100  # Full brightness

    def truncate_text(self, text: str, max_width: int) -> str:
        """
        Truncate text to fit within a given width.
        
        Args:
            text (str): Text to truncate
            max_width (int): Maximum width in pixels
            
        Returns:
            str: Truncated text
        """
        text_width = self.draw.textlength(text, font=self.font)
        
        if text_width <= max_width:
            return text
            
        while text and text_width > max_width:
            text = text[:-1]
            text_width = self.draw.textlength(text, font=self.font)
            
        return text

    def format_time(self, min_value: str) -> str:
        """
        Format the time/status value appropriately.
        
        Args:
            min_value (str): The 'Min' value from the train data
            
        Returns:
            str: Formatted time string
        """
        try:
            int(min_value)
            return f" {min_value}m"
        except ValueError:
            return f" {min_value}"

    def update_display(self, trains: List[Dict]):
        """Update the LED matrix display with train information."""
        # Update brightness based on time of day
        self.update_brightness()
        
        # Clear the image
        self.draw.rectangle((0, 0, self.matrix.width, self.matrix.height), fill=(0, 0, 0))
        
        # Calculate available width for text
        line_indicator_width = 12
        available_width = self.matrix.width - line_indicator_width - 2
        
        # Display each train's information
        y_position = 0
        for train in trains:
            # Get line color
            line_color = get_line_color(train['Line'])
            
            # Draw line indicator
            self.draw.rectangle((0, y_position, 10, y_position + 8), fill=line_color)
            
            # Format destination and time/status
            dest_text = train['Destination']
            time_text = self.format_time(train['Min'])
            
            # Calculate space needed for time
            time_width = self.draw.textlength(time_text, font=self.font)
            
            # Calculate available space for destination
            dest_available_width = available_width - time_width
            
            # Truncate destination if needed
            dest_text = self.truncate_text(dest_text, dest_available_width)
            
            # Draw destination and time
            self.draw.text((line_indicator_width, y_position), 
                         dest_text, 
                         font=self.font, 
                         fill=(255, 255, 255))
            
            # Draw time right after destination
            time_x = line_indicator_width + self.draw.textlength(dest_text, font=self.font)
            self.draw.text((time_x, y_position), 
                         time_text, 
                         font=self.font, 
                         fill=(255, 255, 255))
            
            y_position += 11
        
        # Update the matrix
        self.matrix.SetImage(self.image)
    
def main_loop(config: configparser.ConfigParser):
    """Main program loop."""
    # Initialize display
    display = LEDMatrixDisplay(config['MATRIX'])
    
    # Get WMATA configuration
    api_key = config['WMATA']['api_key']
    station_codes = config['WMATA']['station_codes']
    update_interval = int(config['WMATA'].get('update_interval', 30))
    
    while True:
        try:
            # Get train predictions
            train_predictions = get_train_predictions(station_codes, api_key)
            
            if train_predictions:
                # Update display
                display.update_display(train_predictions)
            else:
                # Show error message if no predictions
                display.draw.rectangle((0, 0, display.matrix.width, display.matrix.height), fill=(0, 0, 0))
                display.draw.text((2, 12), "No trains", font=display.font, fill=(255, 0, 0))
                display.matrix.SetImage(display.image)
            
            # Wait before next update
            time.sleep(update_interval)
            
        except KeyboardInterrupt:
            print("Exiting...")
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    try:
        config = load_config()
        main_loop(config)
    except KeyboardInterrupt:
        print("Program terminated by user")