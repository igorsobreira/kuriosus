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

    @inlineCallbacks
    def assertSavedUrls(self, urls):
        docs = yield self.documents.find()
        found_urls = [doc['url'] for doc in docs]
        self.assertEqual(found_urls, urls)

class MessageHandlerTests(BaseTestCase):

    @inlineCallbacks
    def test_unkown_command(self):
        handler = MessageHandler(self.connection)
        resp = yield handler.handle('foo bar')
        self.assertEqual(handler.messages['unkown_command'], resp)

    @inlineCallbacks
    def test_read_command_should_save_new_link(self):
        handler = MessageHandler(self.connection)
        resp = yield handler.handle('read http://twistedmatrix.com/trac/wiki')
        self.assertEqual('Saved', resp)
        self.assertSavedUrls(['http://twistedmatrix.com/trac/wiki'])

    @inlineCallbacks
    def test_list_command_should_show_all_read_documents(self):
        handler = MessageHandler(self.connection)
        resp1 = yield handler.handle('read http://twistedmatrix.com/trac/wiki')
        resp2 = yield handler.handle('read http://arcturo.com/library')
        self.assertEqual('Saved', resp1)
        self.assertEqual('Saved', resp2)

        resp = yield handler.handle('list')
        self.assertIn('http://twistedmatrix.com/trac/wiki', resp)
        self.assertIn('http://arcturo.com/library', resp)

    @inlineCallbacks
    def test_list_command_shows_message_when_no_documents_found(self):
        handler = MessageHandler(self.connection)
        resp = yield handler.handle('list')
        self.assertIn(handler.messages['no_document_found'], resp)
