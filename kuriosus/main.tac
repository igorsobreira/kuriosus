from __future__ import absolute_import

from twisted.application import service
from twisted.words.protocols.jabber.jid import JID
from twisted.words.xish.domish import Element
from twisted.internet.defer import inlineCallbacks
from wokkel import client, xmppim
import txmongo

from kuriosus.messages import MessageHandler
from kuriosus import settings

jid = JID(settings.JID)
password = settings.JID_PASSWORD

class ParserMessageProtocol(xmppim.MessageProtocol):

    def __init__(self):
        super(ParserMessageProtocol, self).__init__()
        self.connect()

    @inlineCallbacks
    def connect(self):
        self.connection = yield txmongo.MongoConnection()

    @inlineCallbacks
    def onMessage(self, message):
        if not message.body:
            return
        
        handler = MessageHandler(self.connection)
        response = yield handler.handle(unicode(message.body))
        self.answer(message.attributes['from'], response)

    def answer(self, send_to, body):
        response = Element((None, 'message'))
        response['to'] = send_to
        response.addElement('body', content=unicode(body))
        self.send(response)


application = service.Application('XMPP client')

xmppClient = client.XMPPClient(jid, password)
xmppClient.logTraffic = False
xmppClient.setServiceParent(application)

presence = xmppim.PresenceClientProtocol()
presence.setHandlerParent(xmppClient)
presence.available()

message = ParserMessageProtocol()
message.setHandlerParent(xmppClient)
