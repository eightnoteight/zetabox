
""" Minimal helloworld application.
"""

from wheezy.http import HTTPResponse
from wheezy.http import WSGIApplication
from wheezy.routing import url
from wheezy.web.handlers import BaseHandler
from wheezy.web.middleware import bootstrap_defaults
from wheezy.web.middleware import path_routing_middleware_factory
from wheezy.security.crypto import Ticket
from wheezy.security.crypto.comp import aes128
from wheezy.security.crypto.comp import ripemd160
from wheezy.security.crypto.comp import sha1
from wheezy.security.crypto.comp import sha256


class WelcomeHandler(BaseHandler):

    def get(self):
        response = HTTPResponse()
        response.write('Hello World!')
        return response


def welcome(request):
    response = HTTPResponse()
    response.write('Hello World!')
    return response


all_urls = [
    url('', WelcomeHandler, name='default'),
    url('welcome', welcome, name='welcome')
]


options = {}
# Security
options.update({
    'ticket': Ticket(
        max_age=config.getint('crypto', 'ticket-max-age'),
        salt=config.get('crypto', 'ticket-salt'),
        cypher=aes128,
        digestmod=ripemd160 or sha256 or sha1,
        options={
            'CRYPTO_ENCRYPTION_KEY': config.get('crypto', 'encryption-key'),
            'CRYPTO_VALIDATION_KEY': config.get('crypto', 'validation-key')
        }),

    'AUTH_COOKIE': '_a',
    'AUTH_COOKIE_DOMAIN': None,
    'AUTH_COOKIE_PATH': '',
    'AUTH_COOKIE_SECURE': False,

    'XSRF_NAME': '_x',
    'RESUBMISSION_NAME': '_c'
})

main = WSGIApplication(
    middleware=[
        bootstrap_defaults(url_mapping=all_urls),
        path_routing_middleware_factory
    ],
    options=options
)


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    try:
        print('Visit http://localhost:8080/')
        make_server('', 8080, main).serve_forever()
    except KeyboardInterrupt:
        pass
    print('\nThanks!')
