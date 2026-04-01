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
      Row 0:  <air_status>
      Row 13: CO2:  <val> ppm
      Row 26: TVOC: <val> ppb
      Row 39: Temp: <val> C
      Row 52: Hum:  <val> %
    """
    image = Image.new("1", (WIDTH, HEIGHT))
    draw  = ImageDraw.Draw(image)
    font  = ImageFont.load_default()

    temp_str = f"Temp: {temperature:.1f} C" if temperature is not None else "Temp: --.- C"
    hum_str  = f"Hum:  {humidity:.1f} %"   if humidity    is not None else "Hum:  --.- %"

    draw.text((0,  0), air_status,           font=font, fill=255)
    draw.text((0, 13), f"CO2:  {co2} ppm",  font=font, fill=255)
    draw.text((0, 26), f"TVOC: {tvoc} ppb", font=font, fill=255)
    draw.text((0, 39), temp_str,             font=font, fill=255)
    draw.text((0, 52), hum_str,              font=font, fill=255)

    _oled.fill(0)
    _oled.image(image)
    _oled.show()


def clear():
    _oled.fill(0)
    _oled.show()
