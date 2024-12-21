# PrismBerry
Standalone Color E-Ink Display Server &amp; UI for Raspberry Pi

## Installation 

### Prerequisites
Install dependencies
```
sudo apt-get install git gcc python3-dev
```

### Enable SPI
Follow the [instructions](https://www.raspberrypi-spy.co.uk/2014/08/enabling-the-spi-interface-on-the-raspberry-pi/) to enable SPI

### Clone the Repository
``` 
git clone https://github.com/LLukas22/PrismBerry.git
```
### Register Service
```
cd PrismBerry
chmod +x install_service.sh
./install_service.sh
```
This registers the `prismberry.service` service which automatically starts the webserver and pulls updates. 
The web interface is exposed on `http://<RASPBERRY_PI_IP>:8000`.

## Parts
I used the following parts:
- [Raspberry PI Zero 2](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/)
- [7.3inch ACeP 7-Color e-Paper](https://www.waveshare.com/product/7.3inch-e-paper-hat-f.htm)
- [Geekworm X306 V1.3 18650 UPS](https://geekworm.com/products/x306?_pos=7&_sid=ea595b29e&_ss=r)
