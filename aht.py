import adafruit_ens160

# ENS160 is at address 0x52 on this board
_ens = None


def init(i2c):
    global _ens
    _ens = adafruit_ens160.ENS160(i2c, address=0x52)


def set_env_data(humidity, temperature):
    """Feed temperature and humidity to ENS160 for internal compensation."""
    if humidity is not None and temperature is not None:
        _ens.temperature_compensation = temperature
        _ens.humidity_compensation = humidity


def eco2_to_co2(eco2, temperature=25.0, humidity=50.0):
    """
    Convert ENS160 eCO2 reading to estimated CO2 (ppm).

    Algorithm:
      - Temperature correction: +0.2% per degree above 25 C
      - Humidity correction:  -0.1% per % RH above 50 %
    """
    temp_factor = 1 + 0.002 * (temperature - 25.0)
    hum_factor  = 1 - 0.001 * (humidity   - 50.0)
    return round(eco2 * temp_factor * hum_factor)


def read_ens():
    """
    Returns (eco2_raw, tvoc_ppb) when sensor is ready, else (None, None).
    data_validity: 0 = normal, 1 = warm-up, 2 = initial start-up, 3 = invalid
    """
    if _ens.data_validity == 0:
        return _ens.eCO2, _ens.TVOC
    return None, None
