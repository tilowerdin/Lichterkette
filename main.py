import RPi.GPIO as GPIO
import time

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(23, GPIO.OUT)
    
    for i in range(5):
        GPIO.output(23, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(23, GPIO.LOW)
        time.sleep(0.5)
