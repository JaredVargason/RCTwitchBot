'''bot.py'''
import irc.bot
from irc.client import NickMask
import requests
import time
import RPi.GPIO as GPIO
from enum import IntEnum
from datetime import datetime
import operator
from threading import Timer

from settings import TwitchConfig 

TIME_MIN = .5
TIME_MAX = 2

Forward = 11
Backward = 13
Left = 16
Right = 18

GPIO.setmode(GPIO.BOARD)
GPIO.setup(Forward, GPIO.OUT)
GPIO.setup(Backward, GPIO.OUT)
GPIO.setup(Left, GPIO.OUT)
GPIO.setup(Right, GPIO.OUT)

class Government(IntEnum):
    ANARCHY = 0
    DEMOCRACY = 1

class TimeUtils:
    epoch = datetime.utcfromtimestamp(0)

    @classmethod
    def sec_to_ms(cls, seconds):
        return seconds * 1000

    @classmethod
    def ms_to_sec(cls, ms):
        return ms / 1000.0

    @classmethod
    def datetime_to_ms(cls, dt):
        if type(dt) == int or type(dt) == float:
            return dt
        return (dt - TimeUtils.epoch).total_seconds() * 1000.0

    @classmethod
    def ms_difference(cls, dt1, dt2): 
        dt1_ms = cls.datetime_to_ms(dt1)
        dt2_ms = cls.datetime_to_ms(dt2)
        return abs(dt1_ms - dt2_ms)

    @classmethod
    def minutes_to_seconds(cls, m):
        return m * 60

class ElapsedTimer(Timer):
    def __init__(self, interval, function, *args, **kwargs):
        self.start_time = None
        Timer.__init__(self, interval, function, *args, **kwargs)
    
    def start(self):
        self.start_time = datetime.now()
        Timer.start(self)

    def elapsed(self):
        if self.start_time:
            return TimeUtils.ms_difference(self.start_time, datetime.now())

        return None

class Vote:
    def __init__(self, direction, duration):
        self.direction = direction
        self.duration = duration

class Poll:
    def __init__(self, options : list, minutes=15, callback=lambda: None):
        self.option_names = options
        self.votes = [] 
        self.voters = set()

        self.duration = TimeUtils.minutes_to_seconds(minutes)
        self.open = False
        self.timer = None
        self.callback = callback

    def start(self):
        self.open = True
        self.timer = ElapsedTimer(self.duration, self.callback) 
        self.timer.start()

    def end(self):
        self.open = False
        self.timer.cancel() 

    def add_vote(self, voter, option, duration=1):
        if self.open and voter not in self.voters:
            self.votes.append(Vote(option, duration))

    def leader(self) -> int:
        counts = {option: 0 for option in self.option_names}
        for vote in self.votes:
            counts[vote.direction] += 1
        
        maxOption = max(counts.items(), key=operator.itemgetter(1))[0]
        return maxOption

    def average(self, option) -> float:
        durations = [i.duration for i in self.votes] 
        if len(durations):
            return float(sum(durations)) / float(len(durations))
        else:
            return 0

    def restart(self):
        self.end()
        self.clear()
        self.start()

    def clear(self):
        self.votes.clear()

    def __str__(self):
        string = ''
        for i, option in enumerate(self.option_names):
            string += option + ': ' + str(self.votes[i]) + ', '
        return string.rstrip(', ')

class RCTwitchBot(irc.bot.SingleServerIRCBot):

    direction_commands = ['f', 'fr', 'fl', 'b', 'bl', 'br']
    admin_commands = ['mode', 'pause']

    def __init__(self):
        self.username = TwitchConfig.USERNAME
        self.client_id = TwitchConfig.CLIENT_ID
        self.oauth_token = TwitchConfig.OAUTH_TOKEN
        self.channel = '#' + TwitchConfig.CHANNEL
        self.host = TwitchConfig.HOST
        self.port = TwitchConfig.PORT 
        self.superusers = TwitchConfig.SUPERUSERS

        self.government = Government.DEMOCRACY
        self.poll = Poll(RCTwitchBot.direction_commands, .2, self._drive_poll_callback)
        self.paused = False

        self.channel_url = 'https://api.twitch.tv/kraken/users?login=' + self.channel[1:]
        headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(self.channel_url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        print('Connecting to ' + self.host + ' on port ' + str(self.port))
        irc.bot.SingleServerIRCBot.__init__(self, [(self.host, self.port, self.oauth_token)], self.username, self.username)

    def on_welcome(self, c, e):
        #Request capabilities
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)
        print('Joined ' + self.channel)

        self.poll.start()

    def on_pubmsg(self, c, e):
        user = self._get_user(e)
        if e.arguments[0][0] == '!':
            args = e.arguments[0][1:].split(' ')
            cmd = args[0]
            if cmd in self.direction_commands:
                self.do_command(cmd, args, user)

            elif cmd in self.admin_commands:
                self.do_admin_command(cmd, args, user)

    def do_command(self, cmd, args, user):
        if cmd in RCTwitchBot.direction_commands and len(args) == 2:
            try:
                seconds = float(args[1])
                if TIME_MIN <= seconds <= TIME_MAX:
                    if self.government == Government.DEMOCRACY:
                        self.poll.add_vote(user, cmd, seconds)
                    else:
                        self.drive(cmd, seconds)

            except ValueError:
                pass

    def do_admin_command(self, cmd, args, user):
        if user in self.superusers:
            if cmd == 'mode':
                self.mode()
            elif cmd == 'pause':
                self.pause()

    def mode(self):
        if self.government == Government.DEMOCRACY:
            self.poll.end()
            self.poll.clear()

        self.government = Government((self.government + 1) % len(Government))
        self.connection.privmsg(self.channel, "It's a coup!!! Now the government is " + self.government.name)

        if self.government == Government.DEMOCRACY:
            self.poll.start()

    def pause(self):
        self.paused = not self.paused

    def drive(self, cmd, sec):
        if not sec or self.paused:
            return
        print('Executing ' + cmd + str(sec))
        exec('self.' + cmd + '(' + str(sec) + ')')
    
    def _drive_poll_callback(self):
        direction = self.poll.leader()
        duration = self.poll.average(direction) 
        self.drive(direction, duration)
        self.poll.restart() 

    def _get_user(self, e):
        return irc.client.NickMask(e.source).user

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
    bot = RCTwitchBot()
    bot.start()
