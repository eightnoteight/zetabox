import ujson as json
import telebot
import tornado
import textwrap
from concurrent.futures import ThreadPoolExecutor
# check this out
# from ConfigParser import SafeConfigParser
import requests
from pastebot.storage import DatabaseHandler
from pastebot.config import config

bot = telebot.TeleBot(config['zbpastebot_api_token'], threaded=False)

executor = ThreadPoolExecutor(max_workers=5)

@bot.message_handler(commands=['start', 'help'])
@tornado.gen.coroutine
def send_help(message):
    yield executor.submit(bot.send_message, message.chat.message_id, textwrap.dedent(
        """
        ========================================
        /gistauth ::token::
        ----------------------------------------
        to access gist api i.e to create new
        gist please go over this link
        https://github.com/settings/tokens/new
        and create a token and authorize this
        app by copy token and use this command.
        ========================================
        /quickgist ::description::
        ::content::
        ::content::
        ----------------------------------------
        set the description and content of gist
        to quickly create a gist
        ========================================
        /gist
        ----------------------------------------
        start on gist operation.
        ========================================
        /description ::description::
        ----------------------------------------
        set description
        ========================================
        ::upload file::
        ----------------------------------------
        upload multiple file as a part of gist.
        ========================================
        /okgist
        ----------------------------------------
        after setting description and after
        uploading the files pass this command to
        create the gist.
        ========================================
        """
    ))

@bot.message_handler(commands=['gistauth'])
@tornado.gen.coroutine
def gistauth(message):
    _, _, token = message.text.partition(' ')
    if token:
        # blocking operation
        # dispath a request to github, to check the authenticity of the token
        # params: token
        response = yield executor.submit(requests.get, 'https://api.github.com/user', headers={
            'Authorization': 'token {}'.format(token),
        })
        if response.status_code == 200:
            # if 'gist' not in response.headers['X-OAuth-Scopes']
            #     bot.reply_to(message, 'successfully authenticated')
            # else:
            #     bot.reply_to(message, 'invalid token: X-OAuth-Scopes doesn't contain gist)
            userhandle = yield executor.submit(DatabaseHandler, message.from_user.username)
            yield executor.submit(userhandle.setGistAuth, token)  # autosave is on, so yield it.
            yield executor.submit(bot.send_message, message.chat.message_id, "successfully authenticated")
        else:
            yield executor.submit(bot.send_message, message.chat.message_id, "invalid token")
    else:
        yield executor.submit(bot.send_message, message.chat.message_id, textwrap.dedent("""
        ========================================
        /gistauth ::token::
        ----------------------------------------
        to access gist api i.e to create new
        gist please go over this link
        https://github.com/settings/tokens/new
        and create a token and authorize this
        app by copy token and use this command.
        ========================================
        """))

@bot.message_handler(commands=['quickgist'])
@tornado.gen.coroutine
def quickgist(message):
    cmd, _, gist = message.text.partition('\n')
    _, _, description = cmd.partition(' ')
    if gist == '' or description == '':
        yield executor.submit(
            bot.send_message, message.chat.message_id,
            'invalid request:\nempty content or description')
        raise tornado.gen.Return()
    userhandle = yield executor.submit(DatabaseHandler, message.from_user.username)
    data = {
        "description": description,
        "public": False,
        "files": {
            "file.txt": {
                "content": gist
            }
        }
    }
    response = yield executor.submit(
        requests.post,
        'https://api.github.com/gists',
        data=json.dumps(data), headers={
            'authorization': 'token {}'.format(str(userhandle.getGistAuth())),
        })
    if response.status_code == 200:
        html_url = response.json()['html_url']
        shorturl = yield executor.submit(shortenurl, html_url)
        yield executor.submit(bot.send_message, message.chat.message_id, '\n'.join([html_url, shorturl]))
    elif response.status_code == 401:
        yield executor.submit(bot.send_message, message.chat.message_id, "zetabox: 401 unauthorized")
    else:
        # log this event and send the log_id to reproduce the error.
        yield executor.submit(bot.send_message, message.chat.message_id, "got unknown error, report this to admin @eightnoteight")


@bot.message_handler(commands=['description'])
@tornado.gen.coroutine
def setdescription(message):
    _, _, description = message.text.partition(' ')
    if description == '':
        yield executor.submit(bot.send_message, message.chat.message_id, "invalid request:\ndescription can't be empty")
        raise tornado.gen.Return()
    userhandle = yield executor.submit(DatabaseHandler, message.from_user.username)
    yield executor.submit(userhandle.setDescription, description)
    yield executor.submit(bot.send_message, message.chat.message_id, 'description set :)')

@bot.message_handler(commands=['gist'])
@tornado.gen.coroutine
def startgist(message):
    yield executor.submit(
        bot.send_message, message.chat.message_id,
        textwrap.dedent("""
            Ok now set description with
            /description
            and then upload your files
            after that issue
            /okgist to create the gist
        """))


def shortenurl(github_url):
    return requests.post('https://git.io/', {
        'url': github_url,
    }).headers['location']

@bot.message_handler(commands=['okgist'])
@tornado.gen.coroutine
def creategist(message):
    # TODO: assert that the current operation is gist creation operation.
    # TODO: send the typing reply
    userhandle = yield executor.submit(DatabaseHandler, message.from_user.username)
    operationstatus = userhandle.user.operationstatus
    data = {
        "description": operationstatus['description'],
        "public": bool(operationstatus['public']),
        "files": {}
    }
    for key, value in operationstatus.items():
        if key.endswith('file'):
            data['files'][key[:-4]] = {
                'content': value,
            }
    response = yield executor.submit(requests.post, 'https://api.github.com/gists', data=json.dumps(data))
    html_url = response.json()['html_url']
    shorturl = shortenurl(html_url)
    yield executor.submit(bot.send_message, message.chat.message_id, 'url: {}\nshorturl: {}\n'.format(html_url, shorturl))

@bot.message_handler(commands=['pasteauth'])
def pastebinauth(message):
    pass


@bot.message_handler(commands=['paste'])
def startpaste(message):
    pass

@bot.message_handler(commands=['quickpaste'])
def quickpaste(message):
    pass

@bot.message_handler(commands=['okpaste'])
def createpaste(message):
    # dont forget to send the typing reply
    pass

@bot.message_handler(commands=['content'])
def setcontent(message):
    pass

@bot.message_handler(content_types=['document'])
@tornado.gen.coroutine
def receivefile(message):
    # send the fileid to ThreadPool from tornado.concurrent
    file_name = message.document.file_name
    file_info = yield executor.submit(bot.get_file, message.document.file_id)
    response = yield executor.submit(
        requests.get, 'https://api.telegram.org/file/bot{0}/{1}'.format(
            config['zbpastebot_api_token'], file_info.file_path))
    userhandle = yield executor.submit(DatabaseHandler, message.from_user.username)
    userhandle.user.operationstatus[file_name + 'file'] = response.content
    yield executor.submit(userhandle.user.save)
    yield executor.submit(bot.send_message, message.chat.message_id, file_name + ' received!')
