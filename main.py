import time
import board
import busio
import digitalio

import aht as ens_sensor
import ens as aht_sensor
import oled as display

# ── SHARED I2C BUS ────────────────────────────────────────────────────────────
# All three I2C devices (ENS160 @ 0x52, AHT21 @ 0x38, OLED @ 0x3C) share one bus
i2c = busio.I2C(board.SCL, board.SDA)

ens_sensor.init(i2c)
aht_sensor.init(i2c)
display.init(i2c)

# ── LED SETUP ─────────────────────────────────────────────────────────────────
# GPIO17 → green  LED  (Good Air Quality,     CO2 ≤ 1000 ppm)
# GPIO27 → yellow LED  (Mediocre Air Quality, CO2 ≤ 1500 ppm)
# GPIO22 → red    LED  (Bad Air Quality,      CO2  > 1500 ppm)

def _make_led(pin):
    led = digitalio.DigitalInOut(pin)
    led.direction = digitalio.Direction.OUTPUT
    return led

green_led  = _make_led(board.D17)
yellow_led = _make_led(board.D27)
red_led    = _make_led(board.D22)


def classify(co2):
    if co2 <= 1000:
        return "Good Air Quality"
    elif co2 <= 1500:
        return "Mediocre Air Quality"
    else:
        return "Bad Air Quality"


def set_leds(status):
    green_led.value  = (status == "Good Air Quality")
    yellow_led.value = (status == "Mediocre Air Quality")
    red_led.value    = (status == "Bad Air Quality")


def shutdown():
    green_led.value = yellow_led.value = red_led.value = False
    display.clear()


# ── MAIN LOOP ─────────────────────────────────────────────────────────────────
start_time = time.monotonic()
print("Smart Air Meter starting...")
display.clear()
time.sleep(2)

try:
    while True:
        # 1. Read AHT21 (temperature + humidity)
        temperature, humidity = aht_sensor.read_aht()

        # 2. Feed env data to ENS160 for internal compensation
        ens_sensor.set_env_data(humidity, temperature)

        # 3. Read ENS160 (only valid when data_validity == 0)
        eco2_raw, tvoc = ens_sensor.read_ens()

        if eco2_raw is not None:
            # 4. Convert eCO2 → CO2 using temp/humidity correction algorithm
            co2 = ens_sensor.eco2_to_co2(
                eco2_raw,
                temperature if temperature is not None else 25.0,
                humidity    if humidity    is not None else 50.0,
            )

            status = classify(co2)

            # 5. Update LEDs
            set_leds(status)

            # 6. Update OLED
            display.update_display(co2, tvoc, temperature, humidity, status)

            # 7. Serial debug output
            temp_str = f"{temperature:.1f} C" if temperature is not None else "err"
            hum_str  = f"{humidity:.1f} %"    if humidity    is not None else "err"
            print(f"CO2: {co2} ppm | TVOC: {tvoc} ppb | "
                  f"Temp: {temp_str} | Hum: {hum_str} | {status}")
        else:
            elapsed = time.monotonic() - start_time
            print(f"Smart Air Meter starting ({elapsed:.0f}s)")

        time.sleep(2)

except KeyboardInterrupt:
    print("Stopped by user.")

finally:
    shutdown()
