from datetime import datetime, timedelta
from twisted.internet.defer import inlineCallbacks

def findAll():
    return (Help, ShowOldReadDocuments, ShowTodaysReadDocuments, RemoveReadDocument, 
            AddReadDocument)

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


class ShowDocuments(Command):
    '''
    Base class to commands that list documents filtering somehow
    '''
    document_with_title = u' %(title)s\n %(url)s\n'
    document_without_title = u' %(url)s\n'

    title = 'Documents'  # subclasses should implement this

    @inlineCallbacks
    def answer(self):
        docs = yield self.documents.find(self.get_filter_spec())
        urls = []
        for doc in docs:
            if doc['title']:
                urls.append(self.document_with_title % doc)
            else:
                urls.append(self.document_without_title % doc)
        if not urls:
            resp = u"Your read list is still empty."
        else:
            resp = u'\n'+ self.title +':\n\n' + u'\n'.join(urls)

        self.finish(resp)

    def get_filter_spec(self):
        raise NotImplementedError

class ShowTodaysReadDocuments(ShowDocuments):
    pattern = r'^read$'
    doc = u'read: show todays read documents'
    title = u"Today's read documents"

    def get_filter_spec(self):
        today = datetime.now().date()
        today = datetime(today.year, today.month, today.day)
        tomorrow = today + timedelta(days=1)
        return {'date': {'$gte': today, '$lt': tomorrow}}

class ShowOldReadDocuments(ShowDocuments):
    pattern = r'^read yesterday$'
    doc = u'read yesterday: show yesterdays read documents'
    title = u"Yesterday's read documents"

    def get_filter_spec(self):
        today = datetime.now().date()
        today = datetime(today.year, today.month, today.day)
        yesterday = today - timedelta(days=1)
        return {'date': {'$gte': yesterday, '$lt': today}}


class RemoveReadDocument(Command):
    pattern = r'^unread (.*)$'
    doc = 'unread [document url or title]: remove read document (no undo)'

    @inlineCallbacks
    def answer(self, url_or_title):
        docs = yield self.documents.find({'$or': [
                    {'url': url_or_title},
                    {'title': url_or_title},
                    ]})
        length = len(docs)
        plural = '' if length == 1 else 's'
        if length > 0:
            ids = [doc['_id'] for doc in docs]
            yield self.documents.remove({'_id': {'$in': ids} })
        self.finish('%s document%s removed' % (length, plural))
