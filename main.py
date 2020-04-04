import RPi.GPIO as GPIO
import time

if __name__ == '__main__':
    try:
        print(f"setmode to BCM and setup GPIO 23 to OUT")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(23, GPIO.OUT)
        
        for i in range(5):
            print(f"i = {i}")
            GPIO.output(23, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(23, GPIO.LOW)
            time.sleep(0.5)
    finally:
        print(f"cleanup GPIO")
        GPIO.cleanup()
