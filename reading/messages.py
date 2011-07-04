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
            data = message.split(' ', 1)
            if len(data) == 1:
                self.documentRead('')
            else:
                self.documentRead(data[1])
        elif message.startswith('list'):
            self.showAll()
        else:
            self.notFound()
        return self.deferred

    def notFound(self):
        return self.deferred.callback(self.messages['unkown_command'])

    @inlineCallbacks
    def documentRead(self, data):
        data = data.split(' ', 1)
        if len(data) == 1:
            url, title = data[0], None
        elif len(data) == 2:
            url, title = data
        yield self.documents.insert({'url': data[0], 'title': title}, safe=True)
        self.deferred.callback('Saved')
        
    @inlineCallbacks
    def showAll(self):
        docs = yield self.documents.find()
        urls = []
        for doc in docs:
            if doc['title']:
                urls.append(' - %s\n   %s' % (doc['url'], doc['title']))
            else:
                urls.append(' - %s' % doc['url'])
        if not urls:
            resp = self.messages['no_document_found']
        else:
            resp = u'Read documents\n' + u'\n'.join(urls)

        self.deferred.callback(resp)
