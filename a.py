
import RPi.GPIO as GPIO
import Adafruit_DHT
import time

# GPIO pin setup for the MCP3008 ADC
SPICLK = 11
SPIMISO = 9
SPIMOSI = 10
SPICS = 8

# Analog pin assignments for the MQ sensors
mq2_apin = 0
mq3_apin = 1
mq4_apin = 2
mq6_apin = 3
mq7_apin = 4
mq135_apin = 5

# DHT sensor setup
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

def init():
    """Initialize GPIO pins and ADC setup."""
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SPIMOSI, GPIO.OUT)
    GPIO.setup(SPIMISO, GPIO.IN)
    GPIO.setup(SPICLK, GPIO.OUT)
    GPIO.setup(SPICS, GPIO.OUT)

def readadc(adcnum, clockpin, mosipin, misopin, cspin):
    """Read data from the MCP3008 ADC."""
    if adcnum > 7 or adcnum < 0:
        return -1
    GPIO.output(cspin, True)
    GPIO.output(clockpin, False)
    GPIO.output(cspin, False)

    commandout = adcnum
    commandout |= 0x18  # Start bit + single-ended bit
    commandout <<= 3
    for i in range(5):
        if commandout & 0x80:
            GPIO.output(mosipin, True)
        else:
            GPIO.output(mosipin, False)
        commandout <<= 1
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)

    adcout = 0
    for i in range(12):
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
        adcout <<= 1
        if GPIO.input(misopin):
            adcout |= 0x1

    GPIO.output(cspin, True)
    adcout >>= 1  # Ignore the first null bit
    return adcout

def capture_temperature():
    """Capture temperature and humidity from the DHT22 sensor."""
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        if temperature is not None:
            return temperature, humidity
        time.sleep(1)

def read_gas_sensor_continuously():
    """Continuously read gas sensor values and yield them."""
    global mq2,mq3,mq4,mq6,mq7,mq135
    init()
    
    while True:
        mq2 = readadc(mq2_apin, SPICLK, SPIMOSI, SPIMISO, SPICS)
        mq3 = readadc(mq3_apin, SPICLK, SPIMOSI, SPIMISO, SPICS)
        mq4 = readadc(mq4_apin, SPICLK, SPIMOSI, SPIMISO, SPICS)
        mq6 = readadc(mq6_apin, SPICLK, SPIMOSI, SPIMISO, SPICS)
        mq7 = readadc(mq7_apin, SPICLK, SPIMOSI, SPIMISO, SPICS)
        mq135 = readadc(mq135_apin, SPICLK, SPIMOSI, SPIMISO, SPICS)
        # if mq2 != 1024 or mq2 !=1025 and mq3 != 1024 and mq4 != 1024 and mq6 != 1024 and mq7 != 1024 and mq135 != 1024:
        yield (mq2, mq3, mq4, mq6, mq7, mq135)
            
        # else:
        #     pass
        time.sleep(1)  # Delay for 1 second between reads

if __name__ == "__main__":
    try:
        while True:
            temperature, humidity = capture_temperature()
            print(f"Humidity: {round(humidity,2)}%, Temperature: {round(temperature,2)}°C")
            sensor_values = next(read_gas_sensor_continuously())
            print("Sensor readings:", sensor_values)
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()
