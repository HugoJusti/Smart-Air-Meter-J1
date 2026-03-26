import board
import busio
import adafruit_ccs811

# I2C and CCS811 setup
_i2c = busio.I2C(board.SCL, board.SDA)
ccs = adafruit_ccs811.CCS811(_i2c)


def set_env_data(humidity, temperature):
    """Feed temperature and humidity to CCS811 for internal compensation."""
    if humidity is not None and temperature is not None:
        ccs.set_environmental_data(humidity, temperature)


def eco2_to_co2(eco2, temperature=25.0, humidity=50.0):
    """
    Convert CCS811 eCO2 reading to estimated CO2 (ppm).

    Algorithm:
      - Temperature correction: +0.2% per degree above 25 C
        (warmer air slightly inflates the metal-oxide sensor response)
      - Humidity correction:  -0.1% per % RH above 50 %
        (higher moisture absorbs some VOC/CO2 analytes in the sensing layer)

    Both factors are applied multiplicatively to the raw eCO2 value.
    """
    temp_factor = 1 + 0.002 * (temperature - 25.0)
    hum_factor  = 1 - 0.001 * (humidity   - 50.0)
    co2 = eco2 * temp_factor * hum_factor
    return round(co2)


def read_ccs():
    """Returns (eco2_raw, tvoc_ppb) when data is ready, else (None, None)."""
    if ccs.data_ready:
        return ccs.eco2, ccs.tvoc
    return None, None
