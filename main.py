import tornado.ioloop
import tornado.web
import os

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello World!")

def make_app():
    # from pastebot import urls as pastebot_urls
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == '__main__':
    app = make_app()
    app.listen(os.environ['PORT'])
    tornado.ioloop.IOLoop.current().start()
