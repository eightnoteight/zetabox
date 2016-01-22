import tornado.web
from pastebot.botcore import bot
from pastebot.config import config
import ujson as json
import telebot

class MainHandler(tornado.web.RequestHandler):
    def post(self):
        if self.request.headers.get('content-type') == 'application/json':
            data = self.request.body
            update = telebot.types.Update.de_json(data)
            self.finish()
            bot.process_new_messages([update.message])
        else:
            raise tornado.web.HTTPError(
                403, 'How the FUCK are you able to get my fucking api_token')
        # self.write()

    def get(self):
        self.write('How the FUCK are you able to get my fucking api_token')
        self.finish()

urls = [
    ('/' + config['zbpastebot_api_token'], MainHandler)
]
