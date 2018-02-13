'''test.py is used for testing the GPIO pins on the Pi.'''
import RPi.GPIO as GPIO 
import time

Forward = 11
Backward = 13
Left = 16
Right = 18

GPIO.setmode(GPIO.BOARD)
GPIO.setup(Forward, GPIO.OUT)
GPIO.setup(Backward, GPIO.OUT)
GPIO.setup(Left, GPIO.OUT)
GPIO.setup(Right, GPIO.OUT)

def forward(n : int):
    GPIO.output(Forward, GPIO.HIGH)
    print("Forward!")
    time.sleep(n) 
    GPIO.output(Forward, GPIO.LOW)

def backward(n : int):
    GPIO.output(Backward, GPIO.HIGH)
    print("Backing up...")
    time.sleep(n)
    GPIO.output(Backward, GPIO.LOW)

def left(n : int):
    GPIO.output(Left, GPIO.HIGH)
    print('Left.')
    time.sleep(n)
    GPIO.output(Left, GPIO.LOW)

def right(n : int):
    GPIO.output(Right, GPIO.HIGH)
    print('Right!')
    time.sleep(n)
    GPIO.output(Right, GPIO.LOW)

if __name__ == '__main__':
    forward(1)
    left(1) 
    backward(1)
    right(1)
    GPIO.cleanup()
