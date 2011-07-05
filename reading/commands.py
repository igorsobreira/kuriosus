from twisted.internet.defer import inlineCallbacks

class Command(object):
    pattern = r''

    def __init__(self, db, deferred):
        self.documents = db.documents
        self.deferred = deferred
    
    def answer(self, *args):
        raise NotImplementedError

    def finish(self, response):
        self.deferred.callback(response)


class AddReadDocument(Command):
    pattern = r'^read (.*)'

    @inlineCallbacks
    def answer(self, data):
        data = data.split(' ', 1)
        if len(data) == 1:
            url, title = data[0], None
        elif len(data) == 2:
            url, title = data
        yield self.documents.insert({'url': data[0], 'title': title}, safe=True)
        self.finish('Saved')

class ShowAllReadDocuments(Command):
    pattern = r'^list'

    @inlineCallbacks
    def answer(self):
        docs = yield self.documents.find()
        urls = []
        for doc in docs:
            if doc['title']:
                urls.append(' - %s\n   %s' % (doc['url'], doc['title']))
            else:
                urls.append(' - %s' % doc['url'])
        if not urls:
            resp = u"Your read list is still empty."
        else:
            resp = u'Read documents\n' + u'\n'.join(urls)

        self.finish(resp)
        
