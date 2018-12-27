'''bot.py'''
from settings import HOST, PORT, USERNAME, CLIENT_ID, OAUTH_TOKEN, CHANNEL
import irc.bot
import requests
import time

class TwitchTestBot(irc.bot.SingleServerIRCBot):

    def __init__(self, username, client_id, oauth_token, channel):
        self.username = username
        self.client_id = client_id
        self.oauth_token = oauth_token
        self.channel = '#' + channel

        self.channel_url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(self.channel_url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        print('Connecting to ' + HOST + ' on port ' + str(PORT))
        irc.bot.SingleServerIRCBot.__init__(self, [(HOST, PORT, oauth_token)], username, username)


    def on_welcome(self, c, e):
        print('Joining ' + self.channel)

        #Request capabilities
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

        print('Joined ' + self.channel)

    #c is ServerConnection object
    #e is a json about the event
    def on_pubmsg(self, c, e):
        print('c:',c)
        print('e:',e)
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0].split(' ')[0][1:]
            print('Received command: ' + cmd)
            self.do_command(e, cmd)
        return

    def do_command(self, e, cmd):
        return

    def validate_command(self, c, e):
        if e.arguments[0][:1] == '!':
            whole_cmd = e[1:]

if __name__ == '__main__':
    bot = TwitchTestBot(USERNAME, CLIENT_ID, OAUTH_TOKEN, CHANNEL)
    bot.start()

