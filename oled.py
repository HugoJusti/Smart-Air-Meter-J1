import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

WIDTH  = 128
HEIGHT = 64

_oled = None


def init(i2c):
    global _oled
    _oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C)


def update_display(co2, tvoc, temperature, humidity, air_status):
    """
    Render all four sensor readings plus air quality status on the OLED.

    Layout (128x64 px):
      Row 0:  CO2:  <val> ppm
      Row 13: TVOC: <val> ppb
      Row 26: Temp: <val> C
      Row 39: Hum:  <val> %
      Row 52: <air_status>
    """
    image = Image.new("1", (WIDTH, HEIGHT))
    draw  = ImageDraw.Draw(image)
    font  = ImageFont.load_default()

    temp_str = f"Temp: {temperature:.1f} C" if temperature is not None else "Temp: --.- C"
    hum_str  = f"Hum:  {humidity:.1f} %"   if humidity    is not None else "Hum:  --.- %"

    draw.text((0,  0), f"CO2:  {co2} ppm",  font=font, fill=255)
    draw.text((0, 13), f"TVOC: {tvoc} ppb", font=font, fill=255)
    draw.text((0, 26), temp_str,             font=font, fill=255)
    draw.text((0, 39), hum_str,              font=font, fill=255)
    draw.text((0, 52), air_status,           font=font, fill=255)

    _oled.fill(0)
    _oled.image(image)
    _oled.show()


def clear():
    _oled.fill(0)
    _oled.show()
