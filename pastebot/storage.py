from peewee import CharField, Model
from playhouse.postgres_ext import PostgresqlExtDatabase, HStoreField
import urlparse
import ujson as json
import os
from pastebot.config import config
urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(config["database_url"])

pgs_db = PostgresqlExtDatabase(
    url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

class User(Model):
    username = CharField(unique=True)
    gistauth = CharField()
    pastebinauth = CharField()
    operationstatus = HStoreField()
    # operationstatus template
    # {
    #     'operation': 'gist' or 'pastebin',
    #     # gist params
    #     'description': 'gist description',
    #     'public': true or false,
    #     '<num>name': '<file name>',
    #     '<num>content': '<file content>',
    # }
    class Meta:
        database = pgs_db
        db_table = '__test_pastebot__'

pgs_db.connect()
User.create_table(True)

# TODO: make this DatabaseHandler tornado yieldable class
class DatabaseHandler:
    def __init__(self, username, autosave=True):
        self.user, created = User.get_or_create(
            username=username,
            defaults={
                'gistauth': 'null',
                'pastebinauth': '["username", "password"]',  # json.dumps(('username', 'password'))
                'operationstatus': {
                },
            }
        )
        self.autosave = autosave

    def setGistAuth(self, token):
        self.user.gistauth = token
        if self.autosave:
            self.user.save()

    def getGistAuth(self):
        return str(self.user.gistauth)

    def getDescription(self):
        return str(self.user.description)

    def setPastebinAuth(self, username, password):
        self.user.pastebinauth = json.dumps((username, password))
        if self.autosave:
            self.user.save()

    def setDescription(self, description):
        self.user.description = description
        if self.autosave:
            self.user.save()

    def setOperationStatus(self, operationstatus):
        assert isinstance(operationstatus, dict)
        self.user.operationstatus = operationstatus
        if self.autosave:
            self.user.save()

