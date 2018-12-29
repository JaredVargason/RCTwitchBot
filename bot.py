'''bot.py'''
import irc.bot
import requests
import time
import RPi.GPIO as GPIO

from settings import HOST, PORT, USERNAME, CLIENT_ID, OAUTH_TOKEN, CHANNEL

TIME_MIN = .5
TIME_MAX = 1

Forward = 11
Backward = 13
Left = 16
Right = 18

GPIO.setmode(GPIO.BOARD)
GPIO.setup(Forward, GPIO.OUT)
GPIO.setup(Backward, GPIO.OUT)
GPIO.setup(Left, GPIO.OUT)
GPIO.setup(Right, GPIO.OUT)

class RCTwitchBot(irc.bot.SingleServerIRCBot):

    helpList = ['faq', 'help', 'commands']

    def __init__(self, username, client_id, oauth_token, channel):
        '''Available commands: fr, fl, f, br, bl, b'''
        self.username = username
        self.client_id = client_id
        self.oauth_token = oauth_token
        self.channel = '#' + channel

        self.channel_url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(self.channel_url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        print('Connecting to ' + HOST + ' on port ' + str(PORT))
        irc.bot.SingleServerIRCBot.__init__(self, [(HOST, PORT, oauth_token)], 'gits', 'gits')

        self.directionDict = {'f' : RCTwitchBot.f, 'fr' : RCTwitchBot.fr, 'fl' : RCTwitchBot.fl,
                            'b' : RCTwitchBot.b, 'br' : RCTwitchBot.br, 'bl' : RCTwitchBot.bl}

    def on_welcome(self, c, e):
        print('Joining ' + self.channel)

        #Request capabilities
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)
        print('Joined ' + self.channel)

    def on_pubmsg(self, c, e):
        if e.arguments[0][0] == '!':
            args = e.arguments[0][1:].split(' ')
            key = args[0]
            if key in self.directionDict.keys():
                self.drive(key, args)
            elif key in RCTwitchBot.helpList:
                self.helpMsg()

    def drive(self, cmd, args):
        func = self.directionDict[cmd]
        try:
            seconds = float(args[1])
            if seconds >= TIME_MIN and seconds <= TIME_MAX:
                func(self, seconds) 
        except:
            return
        print('Successful drive')

    def helpMsg(self):
        c = self.connection
        c.privmsg(self.channel, 'Check below for commands, you tooty fruit')

    def f(self, sec: float):
        GPIO.output(Forward, GPIO.HIGH)
        time.sleep(sec)
        GPIO.output(Forward, GPIO.LOW)

    def b(self, sec: float):
        GPIO.output(Backward, GPIO.HIGH)
        time.sleep(sec)
        GPIO.output(Backward, GPIO.LOW)

    def fr(self, sec: float):
        GPIO.output(Forward, GPIO.HIGH)
        GPIO.output(Right, GPIO.HIGH)
        time.sleep(sec)
        GPIO.output(Forward, GPIO.LOW)
        GPIO.output(Right, GPIO.LOW)

    def fl(self, sec: float):
        GPIO.output(Forward, GPIO.HIGH)
        GPIO.output(Left, GPIO.HIGH)
        time.sleep(sec)
        GPIO.output(Forward, GPIO.LOW)
        GPIO.output(Left, GPIO.LOW)

    def br(self, sec: float):
        GPIO.output(Backward, GPIO.HIGH)
        GPIO.output(Right, GPIO.HIGH)
        time.sleep(sec)
        GPIO.output(Backward, GPIO.LOW)
        GPIO.output(Right, GPIO.LOW)

    def bl(self, sec: float):
        GPIO.output(Backward, GPIO.HIGH)
        GPIO.output(Left, GPIO.HIGH)
        time.sleep(sec)
        GPIO.output(Backward, GPIO.LOW)
        GPIO.output(Left, GPIO.LOW)

if __name__ == '__main__':
    bot = RCTwitchBot(USERNAME, CLIENT_ID, OAUTH_TOKEN, CHANNEL)
    bot.start()
