import re
import types

import txmongo
from twisted.internet.defer import inlineCallbacks, Deferred

from reading import settings
from reading import commands

class MessageHandler(object):

    messages = {
        'unkown_command': u"Unkown Command",
        }

    def __init__(self, connection):
        self.deferred = None
        self.connection = connection
        self.documents = self.connection[settings.DBNAME].documents

    def handle(self, message):
        self.deferred = Deferred()
        commandList = self.findCommands()
        for command in commandList:
            pattern = re.compile(command.pattern)
            match = pattern.match(message)
            if match:
                args = match.groups()
                command(self.connection[settings.DBNAME], self.deferred).answer(*args)
                break
        else:
            self.notFound()
        return self.deferred

    def findCommands(self):
        commandList = []
        for objname in dir(commands):
            obj = getattr(commands, objname)
            if self.isCommand(obj):
                commandList.append(obj)
        return commandList

    def isCommand(self, obj):
        return isinstance(obj, type) and issubclass(obj, commands.Command) and \
            obj is not commands.Command

    def notFound(self):
        return self.deferred.callback(self.messages['unkown_command'])
