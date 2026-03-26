import adafruit_ahtx0

# AHT21 is at address 0x38 on this board (shares I2C bus with ENS160)
_aht = None


def init(i2c):
    global _aht
    _aht = adafruit_ahtx0.AHTx0(i2c)


def read_aht():
    """
    Read temperature (Celsius) and humidity (%) from the AHT21.
    Returns (temperature, humidity), or (None, None) on error.
    """
    try:
        temperature = _aht.temperature
        humidity    = _aht.relative_humidity
        return temperature, humidity
    except RuntimeError:
        return None, None
