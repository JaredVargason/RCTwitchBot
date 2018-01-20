'''bot.py'''
from settings import HOST, PORT, USERNAME, CLIENT_ID, OAUTH_TOKEN, CHANNEL
import irc.bot
import requests

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
        return
        

if __name__ == '__main__':
    bot = RCTwitchBot(USERNAME, CLIENT_ID, OAUTH_TOKEN, CHANNEL)
    bot.start()