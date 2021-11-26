from peerbot.MessagePacker import MessagePacker
from peerbot.MessageUnpacker import MessageUnpacker

from abc import ABC
from abc import abstractmethod
import asyncio

class PeerBotState(ABC, MessagePacker, MessageUnpacker):

    def __init__(self, stateMachine, logger):
        self.logger = logger
        self.stateMachine = stateMachine
        self.userId = self.stateMachine.getUser().id
        self.ownId = self.stateMachine.getOwnId()
        
    @abstractmethod
    def start(self):
        pass
        
    def execute(self, message):
        self.logger.trace("execute called")
        if(self._isMessageFromOwnAccount(message)):
            self.logger.trace("unpacking message")
            signalNumber, senderUserIdStr, content, comments = self._unpackMessage(message.content)
            messageContent = self._unpackMessage(message.content)

            if(self._isMessageFromOwnClient(messageContent["userId"])):
                self.logger.debug("Processing message. messageContent: " + str(messageContent))
                self._processMessage(messageContent)

    def _isMessageFromOwnClient(self, senderUserId):
        return senderUserId != self.userId
        
    def _isMessageFromOwnAccount(self, message):
        return message.author.id == self.ownId
        
    def _sendMessage(self, message):
        asyncio.ensure_future(self.stateMachine.getProtocolChannel().send(message))
        
    def _broadcastPriorityNumberDeclarationIfPriorityNumberIsConflicting(self, receivedPriorityNumber):
        ownPriorityNumber = self.stateMachine.getPriorityNumber()
        self.logger.trace("_broadcastPriorityNumberDeclarationIfPriorityNumberIsConflicting called. ownPriorityNumber: " + str(ownPriorityNumber) + ", receivedPriorityNumber: " + str(receivedPriorityNumber))
        if(ownPriorityNumber == int(receivedPriorityNumber)):
            self.logger.trace("ownPriorityNumber == receivedPriorityNumber")
            self._broadcastPriorityNumberIsConflictingSignal()
    
    def _broadcastPriorityNumberIsConflictingSignal(self):
        self.logger.trace("_broadcastPriorityNumberIsConflictingSignal called")

        message = self._packPriorityNumberIsConflictingMessage()
        self._sendMessage(message)
        
    @abstractmethod
    async def _processMessage(self, signalNumber, senderId, content):
        pass
        
    