'''bot.py'''
from settings import HOST, PORT, USERNAME, CLIENT_ID, OAUTH_TOKEN, CHANNEL
import irc.bot
import requests
import RPi.GPIO as GPIO

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
            cmd = e.arguments[0].split(' ')[0][1:]
            print('Received command: ' + cmd)
            self.do_command(e, cmd)

    '''Available commands: fr, fl, f, br, bl, b'''
    def do_command(self, e, cmd):
        if cmd == 'f':
            forward(MOVE_TIME)

        elif cmd == 'fr':
            forwardright(MOVE_TIME)
        
        elif cmd == 'fl':
            forwardleft(MOVE_TIME)

        elif cmd == 'b':
            backward(MOVE_TIME)

        elif cmd == 'br':
            backwardright(MOVE_TIME)

        elif cmd == 'bl':
            backwardleft(MOVE_TIME)

        else:
            print('bad command: ' + str(cmd))

    def forward(n : int):
        GPIO.output(Forward, GPIO.HIGH)
        time.sleep(n)
        GPIO.output(Forward, GPIO.LOW)

    def backward(n : int):
        GPIO.output(Backward, GPIO.HIGH)
        time.sleep(n)
        GPIO.output(Backward, GPIO.LOW)

    def forwardright(n : int):
        GPIO.output(Forward, GPIO.HIGH)
        GPIO.output(Right, GPIO.HIGH)
        time.sleep(n)
        GPIO.output(Forward, GPIO.LOW)
        GPIO.output(Right, GPIO.LOW)

    def forwardleft(n : int):
        GPIO.output(Forward, GPIO.HIGH)
        GPIO.output(Left, GPIO.HIGH)
        time.sleep(n)
        GPIO.output(Forward, GPIO.LOW)
        GPIO.output(Left, GPIO.LOW)

    def backwardright(n : int):
        GPIO.output(Backward, GPIO.HIGH)
        GPIO.output(Right, GPIO.HIGH)
        time.sleep(n)
        GPIO.output(Backward, GPIO.LOW)
        GPIO.output(Right, GPIO.LOW)

    def backwardleft(n : int):
        GPIO.output(Backward, GPIO.HIGH)
        GPIO.output(Left, GPIO.HIGH)
        time.sleep(n)
        GPIO.output(Backward, GPIO.LOW)
        GPIO.output(Left, GPIO.LOW)

if __name__ == '__main__':
    bot = RCTwitchBot(USERNAME, CLIENT_ID, OAUTH_TOKEN, CHANNEL)
    bot.start()
