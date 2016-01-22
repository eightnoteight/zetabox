import pastebot
import tornado.ioloop
import tornado.web
import os

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello World!")

def resolveurls(prefix, urls):
    return [('/{}{}'.format(prefix, x), y) for x, y in urls]

def make_app():
    urls = reduce(list.__add__, [
        [(r'/', MainHandler)],
        resolveurls('pastebot', pastebot.urls),
    ])
    return tornado.web.Application(urls)

if __name__ == '__main__':
    app = make_app()
    app.listen(os.environ['PORT'])
    tornado.ioloop.IOLoop.current().start()
