

from machine import Pin,I2C
from bmp280 import *
import tm1637
import urequests
import network, time

# Read credentials from iot_credentials.py 
from iot_credentials import THINGSPEAK_WRITE_API_KEY, ssid, password

# Acender o LED do PICO:
led = machine.Pin("LED", machine.Pin.OUT)
led.on()




# Configure Display
tm = tm1637.TM1637(clk=Pin(5), dio=Pin(4))
tm.write([0, 0, 0, 0]) # all LEDS off

# Configure Pico W as Station
sta_if=network.WLAN(network.STA_IF)
sta_if.active(True)
 
if not sta_if.isconnected():
    print('connecting to network...')
    tm.show('wait')
    sta_if.connect(ssid, password)
    while not sta_if.isconnected():
     pass

print('network config:', sta_if.ifconfig())
tm.show('good')
time.sleep(0.3)
  
#Configre Sensor:
sdaPIN=machine.Pin(0)
sclPIN=machine.Pin(1)
bus = I2C(0,sda=sdaPIN, scl=sclPIN, freq=400000)
time.sleep(0.3)
bmp = BMP280(bus)
bmp.use_case(BMP280_CASE_INDOOR)
    
while True:
    try:
        pressure=bmp.pressure # Tenta obter uma nova leitura do sensor.
    except Exception as e:
       print("Sensor reading error: ", e) # Se der erro mostra o erro.
       tm.show('Err0')
    else:
        #Se não há erros mostra a pressão:
        pDisplay = round(pressure / 100) #Arredonda e mostra a pressão no dispay. 
        print("Pressure: {} Pa".format(pressure))
        print("Pressure rounded: {} hPa".format(pDisplay))
        tm.number(pDisplay)
        
        # Check if wifi connection is still on if not connect again:
        if not sta_if.isconnected():
            print('connecting to network...')
            tm.show('wait')
            sta_if.connect(ssid, password)
            while not sta_if.isconnected():
             pass
        #print('network config:', sta_if.ifconfig())
        #tm.show('good')
        #Send data to Thingspeak:
        if sta_if.isconnected():
            try:
                request = urequests.post( 'https://api.thingspeak.com/update?api_key=' + THINGSPEAK_WRITE_API_KEY + '&field1=' + str(pressure))
                request.close()
            except Exception as e:
               print("Network error: ", e) # Se der erro mostra o erro.
               tm.show('Err1')
               
            else:
                print("...")
                time.sleep(60)
    finally:
        tm.write([0, 0, 0, 0]) # all LEDS off
        time.sleep(0.8)
        