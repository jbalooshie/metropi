# metropi

This is an evolution of a project I built in spring 2024, [buspi](https://github.com/jbalooshie/buspi). While buspi displayed the times for a nearby MTA bus stop, metropi displays the times for a nearby WMATA metro station.

Key Features:

- Runs on a Raspberry Pi 3 A+ and a 32x64 LED matrix panel.
- Shows the status of next 3 trains going in either direction.
- Refreshes with updated information every 30 seconds.
- Dims by 50% from 10pm-5am.
- Uses a config.ini file that can be modified for a differnt station, LED panel size, and update frequency.

**BIG DISCLAIMER**: The majority of this code was generated using Claude 3.5 Sonnet, and is not my original work. You can see my original work on the previous project, linked above.

## Hardware Needed

To run this project, you will need:

1. An [LED Matrix](https://www.adafruit.com/product/2278). I used the linked 32x64, but any similar LED panel should work.
2. A [Raspberry Pi computer](https://www.raspberrypi.com/products/). I used a 3 Model A+, but a 4 Model B would work as well. Note the Python library I used has not been tested with the newer 5s.
3. An [SD Card](https://www.amazon.com/dp/B09X7BK27V?ref=ppx_yo2ov_dt_b_fed_asin_title). You don't need a ton of storage for this, but SDs are cheap so you might as well pick up a larger one you can use for other projects.
4. Power Supply
5. WMATA API Key

You will also need a way to hook the matrix up to the Pi. I used the [Adafruit RGB Matrix Bonnet](https://www.adafruit.com/product/3211). There are other solutions out there, and you can also wire the Matrix directly to the board. If you go the Bonnet route, I'd also recommend grabbing a [Socket Riser Header](https://www.adafruit.com/product/4079). The 3 A+ and 4 don't have enough space for the Bonnet to fit flush on its own. You can get it to sit on the 3 A+ with out, but it is a bit sketchy.

## Setup

Once you have the hardware, go ahead an install Raspberry Pi OS on your SD card. The software to do this can be found [here](https://www.raspberrypi.com/software/). Make sure to install a headless distribution (no desktop enviornment). I used Raspberry Pi OS Lite. We are going to use SSH to set up the project, so you should also configure the wireless options and enable SSH during the OS install.

Once the OS is installed, login to your Pi and run the following commands:

```text
sudo apt update
sudo apt upgrade
sudo apt install git
git clone https://github.com/jbalooshie/metropi.git
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
sudo apt-get update && sudo apt-get install python3-dev cython3 -y
make build-python 
sudo make install-python 
```

And you are good to go! Navigate to the metropi folder and run the command `sudo python app.py`. This will run the app. If you have never run the app before, it will create the config file in the same folder you ran the command from. Update the config file with you API Key and preferred stop to monitor, save it, and then run the app again.

If you would like the app to run on startup, you can use systemd. Update `metropi-display.service` with the path to your metropi folder and path to the app. Then run the following commands:

```text
sudo cp metropi-display.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/metropi-display.service
sudo systemctl daemon-reload
sudo systemctl enable wmata-display.service
sudo systemctl start wmata-display.service
```

This will start the app when the pi boots up.
