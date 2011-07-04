
import txmongo
from twisted.internet.defer import inlineCallbacks, Deferred

from reading import settings

class MessageHandler(object):

    messages = {
        'no_document_found': u"Your read list is still empty.",
        'unkown_command': u"Unkown Command",
        }

    def __init__(self, connection):
        self.deferred = None
        self.connection = connection
        self.documents = self.connection[settings.DBNAME].documents

    def handle(self, message):
        self.deferred = Deferred()
        if message.startswith('read'):
            data = message.split(' ', 1)[1:]
            self.documentRead(data)
        elif message.startswith('list'):
            self.showAll()
        else:
            self.notFound()
        return self.deferred

    def notFound(self):
        return self.deferred.callback(self.messages['unkown_command'])

    @inlineCallbacks
    def documentRead(self, data):        
        yield self.documents.insert({'url': data[0]}, safe=True)
        self.deferred.callback('Saved')
        
    @inlineCallbacks
    def showAll(self):
        docs = yield self.documents.find()
        urls = [u' - %s' % doc['url'] for doc in docs]
        if not urls:
            resp = self.messages['no_document_found']
        else:
            resp = u'Read documents\n' + u'\n'.join(urls)

        self.deferred.callback(resp)
