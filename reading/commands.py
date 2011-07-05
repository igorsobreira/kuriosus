from datetime import datetime
from twisted.internet.defer import inlineCallbacks

def findAll():
    return (AddReadDocument, ShowAllReadDocuments, Help)

class Command(object):
    pattern = r''
    doc = u''

    def __init__(self, db, deferred):
        self.documents = db.documents
        self.deferred = deferred
    
    def answer(self, *args):
        raise NotImplementedError

    def finish(self, response):
        self.deferred.callback(response)


class Help(Command):
    pattern = r'^help$'
    doc = u'help: show this help message'

    def answer(self):
        docs = u'\n - '.join(cmd.doc for cmd in findAll())
        msg = u'Available commands:\n - ' + docs
        self.finish(msg)

class AddReadDocument(Command):
    pattern = r'^read (.*)'
    doc = u'read [document url] [document title]: save read document. title is optional'

    @inlineCallbacks
    def answer(self, data):
        data = data.split(' ', 1)
        if len(data) == 1:
            url, title = data[0], None
        elif len(data) == 2:
            url, title = data
        yield self.documents.insert({'url': data[0], 
                                     'title': title,
                                     'date': datetime.now()}, safe=True)
        self.finish('Saved')

class ShowAllReadDocuments(Command):
    pattern = r'^read$'
    doc = u'read: show all read documents'

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
        
