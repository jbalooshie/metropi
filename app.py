import requests
import time
from typing import List, Dict
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont
import threading
import configparser
import os

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
        
        # Create a blank image for drawing
        self.image = Image.new('RGB', (self.matrix.width, self.matrix.height))
        self.draw = ImageDraw.Draw(self.image)
        
        # Try to load a font
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 8)
        except:
            self.font = ImageFont.load_default()
    
    def update_display(self, trains: List[Dict]):
        """Update the LED matrix display with train information."""
        # Clear the image
        self.draw.rectangle((0, 0, self.matrix.width, self.matrix.height), fill=(0, 0, 0))
        
        # Display each train's information
        y_position = 0
        for train in trains:
            # Get line color
            line_color = get_line_color(train['Line'])
            
            # Draw line indicator
            self.draw.rectangle((0, y_position, 10, y_position + 8), fill=line_color)
            
            # Draw train information
            text = f"{train['Destination']} {train['Min']}min"
            self.draw.text((12, y_position), text, font=self.font, fill=(255, 255, 255))
            
            y_position += 11  # Space between trains
        
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