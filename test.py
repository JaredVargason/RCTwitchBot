'''test.py is used for testing the GPIO pins on the Pi.'''
import RPi.GPIO as gpio
import time

Forward = 11
Backward = 13

gpio.cleanup()

gpio.setmode(gpio.board)
gpio.setup(Forward, gpio.OUT)
gpio.setup(Backward, gpio.OUT)

def forward(n : int):
    gpio.output(Forward, gpio.HIGH)
    print("Forward!")
    time.sleep(n) 
    gpio.output(Forward, gpio.LOW)

def backward(n : int):
    gpio.output(Backward, gpio.HIGH)
    print("Backing up...")
    time.sleep(n)
    gpio.output(Backward, gpio.LOW)

def left():
    pass

def right():
    pass

if __name__ == '__main__':
    forward(2)