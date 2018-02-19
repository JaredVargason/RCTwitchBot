'''bot.py'''
from settings import HOST, PORT, USERNAME, CLIENT_ID, OAUTH_TOKEN, CHANNEL
import irc.bot
import requests
import RPi.GPIO as GPIO
import time

Forward = 11
Backward = 13
Left = 16
Right = 18

MOVE_TIME = 1 

GPIO.setmode(GPIO.BOARD)
GPIO.setup(Forward, GPIO.OUT)
GPIO.setup(Backward, GPIO.OUT)
GPIO.setup(Left, GPIO.OUT)
GPIO.setup(Right, GPIO.OUT)

class RCTwitchBot(irc.bot.SingleServerIRCBot):

    def __init__(self, username, client_id, oauth_token, channel):
        self.username = username
        self.client_id = client_id
        self.oauth_token = oauth_token
        self.channel = '#' + channel

        self.channel_url = 'https://api.twitch.tv/kraken/users?login=' + channel
        print('Connecting to ' + HOST + ' on port ' + str(PORT))
        irc.bot.SingleServerIRCBot.__init__(self, [(HOST, PORT, oauth_token)], username, username)

    def on_welcome(self, c, e):
        print('Joining ' + self.channel)

        #Request capabilities
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

    def on_pubmsg(self, c, e):
        if e.arguments[0][:1] == '!':
            whole_cmd = e.arguments[0].split(' ')
            if len(whole_cmd) == 2:
                cmd = whole_cmd[0][1:]
                time = float(whole_cmd[1])
                if time >= 0.2 and time <= 1:
                    self.do_command(e, cmd, time)


    '''Available commands: fr, fl, f, br, bl, b'''
    def do_command(self, e, cmd, time):
        if cmd == 'f':
            self.forward(time)

        elif cmd == 'fr':
            self.forwardright(time)
        
        elif cmd == 'fl':
            self.forwardleft(time)

        elif cmd == 'b':
            self.backward(time)

        elif cmd == 'br':
            self.backwardright(time)

        elif cmd == 'bl':
            self.backwardleft(time)

        else:
            print('bad command: ' + str(cmd))

    def forward(self, n : float):
        GPIO.output(Forward, GPIO.HIGH)
        time.sleep(n)
        GPIO.output(Forward, GPIO.LOW)

    def backward(self, n : float):
        GPIO.output(Backward, GPIO.HIGH)
        time.sleep(n)
        GPIO.output(Backward, GPIO.LOW)

    def forwardright(self, n : float):
        GPIO.output(Forward, GPIO.HIGH)
        GPIO.output(Right, GPIO.HIGH)
        time.sleep(n)
        GPIO.output(Forward, GPIO.LOW)
        GPIO.output(Right, GPIO.LOW)

    def forwardleft(self, n : float):
        GPIO.output(Forward, GPIO.HIGH)
        GPIO.output(Left, GPIO.HIGH)
        time.sleep(n)
        GPIO.output(Forward, GPIO.LOW)
        GPIO.output(Left, GPIO.LOW)

    def backwardright(self, n : float):
        GPIO.output(Backward, GPIO.HIGH)
        GPIO.output(Right, GPIO.HIGH)
        time.sleep(n)
        GPIO.output(Backward, GPIO.LOW)
        GPIO.output(Right, GPIO.LOW)

    def backwardleft(self, n : float):
        GPIO.output(Backward, GPIO.HIGH)
        GPIO.output(Left, GPIO.HIGH)
        time.sleep(n)
        GPIO.output(Backward, GPIO.LOW)
        GPIO.output(Left, GPIO.LOW)

if __name__ == '__main__':
    bot = RCTwitchBot(USERNAME, CLIENT_ID, OAUTH_TOKEN, CHANNEL)
    bot.start()
