import os
config = {key.lower():value for key, value in os.environ.items()}  #
# config = dict(configparser.items(u'production'))  #
