from datetime import datetime

from twisted.trial import unittest
from twisted.internet.defer import inlineCallbacks

import txmongo

from reading.messages import MessageHandler
from reading import settings

class BaseTestCase(unittest.TestCase):

    @inlineCallbacks
    def setUp(self):
        self.replaceDBNAME()
        self.connection = yield txmongo.MongoConnection()
        self.documents = self.connection[settings.DBNAME].documents
        yield self.documents.drop()

    @inlineCallbacks
    def tearDown(self):
        self.restoreDBNAME()
        yield self.connection.disconnect()

    def replaceDBNAME(self):
        self.original_DBNAME = settings.DBNAME
        settings.DBNAME = settings.DBNAME + '_test'

    def restoreDBNAME(self):
        settings.DBNAME = self.original_DBNAME

class MessageHandlerTests(BaseTestCase):

    @inlineCallbacks
    def test_unkown_command(self):
        handler = MessageHandler(self.connection)
        resp = yield handler.handle('foo bar')
        self.assertEqual(handler.messages['unkown_command'], resp)

    # read (link) [title]

    @inlineCallbacks
    def test_read_command_should_save_new_url(self):
        handler = MessageHandler(self.connection)
        resp = yield handler.handle('read http://twistedmatrix.com/trac/wiki')
        urls = yield self.documents.find({'url': 'http://twistedmatrix.com/trac/wiki'})
        def format(d):
            return d.strftime('d/m/Y')

        self.assertEqual('Saved', resp)
        self.assertEqual(1, len(urls))
        self.assertEqual(format(urls[0]['date']), format(datetime.now()))

    @inlineCallbacks
    def test_read_command_should_save_url_with_title(self):
        handler = MessageHandler(self.connection)
        resp = yield handler.handle('read http://www.mnot.net/cache_docs/ '
                                    'Web Caching Docs')
        urls = yield self.documents.find({'url': 'http://www.mnot.net/cache_docs/',
                                          'title': 'Web Caching Docs'})
        self.assertEqual('Saved', resp)
        self.assertEqual(1, len(urls))

    # read

    @inlineCallbacks
    def test_empty_read_command_should_show_all_read_documents(self):
        handler = MessageHandler(self.connection)
        resp1 = yield handler.handle('read http://twistedmatrix.com/trac/wiki')
        resp2 = yield handler.handle('read http://www.mnot.net/cache_docs/ '
                                     'Web Caching Docs')

        self.assertEqual('Saved', resp1)
        self.assertEqual('Saved', resp2)

        resp1 = yield handler.handle('read')
        resp2 = yield handler.handle(' read  ')
        self.assertEqual(resp1, resp2)
        self.assertIn('Read documents', resp1)
        self.assertIn('http://twistedmatrix.com/trac/wiki', resp1)
        self.assertIn('http://www.mnot.net/cache_docs/', resp1)
        self.assertIn('Web Caching Docs', resp1)

    @inlineCallbacks
    def test_empty_read_command_shows_message_when_no_documents_found(self):
        handler = MessageHandler(self.connection)
        resp = yield handler.handle('read')
        self.assertIn(u'Your read list is still empty', resp)

    # help

    @inlineCallbacks
    def test_help_command(self):
        handler = MessageHandler(self.connection)
        resp = yield handler.handle('help')
        self.assertIn('Available commands:', resp)
        self.assertIn(' - read', resp)
        self.assertIn(' - help', resp)

    # unread (url|title)

    @inlineCallbacks
    def test_unread_command_should_remove_by_url(self):
        handler = MessageHandler(self.connection)
        resp = yield handler.handle('read http://twistedmatrix.com/trac/wiki')
        self.assertEqual('Saved', resp)

        count = yield self.documents.count()
        self.assertEqual(1, count)

        resp = yield handler.handle('unread http://twistedmatrix.com/trac/wiki')
        self.assertEqual('1 document removed', resp)

        count = yield self.documents.count()
        self.assertEqual(0, count)

    @inlineCallbacks
    def test_unread_command_should_remove_by_title(self):
        handler = MessageHandler(self.connection)
        resp = yield handler.handle('read http://twistedmatrix.com/trac/wiki '
                                    'Twisted Wiki')
        self.assertEqual('Saved', resp)

        count = yield self.documents.count()
        self.assertEqual(1, count)

        resp = yield handler.handle('unread Twisted Wiki')
        self.assertEqual('1 document removed', resp)

        count = yield self.documents.count()
        self.assertEqual(0, count)

    @inlineCallbacks
    def test_unread_command_shouldnt_remove_anything_if_not_found(self):
        handler = MessageHandler(self.connection)
        resp1 = yield handler.handle('read http://twistedmatrix.com/trac/wiki')
        resp2 = yield handler.handle('read http://www.mnot.net/cache_docs/ '
                                     'Web Caching Docs')
        count = yield self.documents.count()
        self.assertEqual(2, count)
        
        resp = yield handler.handle('unread nothing')
        self.assertEqual('0 documents removed', resp)

        count = yield self.documents.count()
        self.assertEqual(2, count)

    @inlineCallbacks
    def test_unread_command_should_remove_all_docs_found(self):
        handler = MessageHandler(self.connection)
        resp1 = yield handler.handle('read http://twistedmatrix.com/trac/wiki '
                                     'Good doc')
        resp2 = yield handler.handle('read http://www.mnot.net/cache_docs/ '
                                     'Good doc')
        count = yield self.documents.count()
        self.assertEqual(2, count)
        
        resp = yield handler.handle('unread Good doc')
        self.assertEqual('2 documents removed', resp)

        count = yield self.documents.count()
        self.assertEqual(0, count)
