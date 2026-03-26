import board
import adafruit_dht

# DHT22 data pin connected to GPIO18 (Pin 12)
_dht_device = adafruit_dht.DHT22(board.D18, use_pulseio=False)


def read_dht():
    """
    Read temperature (Celsius) and humidity (%) from the DHT22.
    Returns (temperature, humidity), or (None, None) on a read error.
    DHT sensors occasionally produce transient errors — callers should
    simply reuse the last valid reading when None is returned.
    """
    try:
        temperature = _dht_device.temperature
        humidity    = _dht_device.humidity
        return temperature, humidity
    except RuntimeError:
        return None, None
