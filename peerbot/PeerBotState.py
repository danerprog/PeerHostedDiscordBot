from abc import ABC
from abc import abstractmethod

class PeerBotState(ABC):

    def __init__(self, stateMachine, logger):
        self.logger = logger
        self.stateMachine = stateMachine
        self.userId = self.stateMachine.getUser().id
        
    @abstractmethod
    async def start(self):
        pass
        
    async def execute(self, message):
        self.logger.trace("execute called")
        protocolNumber, senderUserId, content, comments = self._unpackMessage(message.content)
        senderUserIdInt = int(senderUserId)
        
        if(senderUserIdInt != self.userId):
            self.logger.debug("Processing message. protocolNumber: " + protocolNumber + ", senderUserId: " + senderUserId + ", content: " + content)
            await self._processMessage(int(protocolNumber), senderUserIdInt, content)

    def _createMessage(self, protocolNumber, content = '', comments = None):
        self.logger.trace("_createMessage called")
        message = '[' + str(protocolNumber) + ' ' + str(self.userId) + ' ' + str(content) + ']'
        if comments != None:
            message += ' ' + str(comments)
        self.logger.debug("Message created. message: " + message)
        return message
        
    def _unpackMessage(self, message):
        self.logger.trace("_unpackMessage called")
        importantMessage, comments = message.split("]", 2)
        protocolNumber, userId, content = importantMessage[1:].split(" ", 3)
        return protocolNumber, userId, content, comments
        
    async def _send302IfPriorityNumberIsConflicting(self, receivedPriorityNumber):
        ownPriorityNumber = self.stateMachine.getPriorityNumber()
        self.logger.debug("_send302IfPriorityNumberIsConflicting called. ownPriorityNumber: " + str(ownPriorityNumber) + ", receivedPriorityNumber: " + str(receivedPriorityNumber))
        if(ownPriorityNumber == int(receivedPriorityNumber)):
            self.logger.debug("ownPriorityNumber == receivedPriorityNumber")
            await self.stateMachine.getProtocolChannel().send(self._createMessage(302, ''))
        
    @abstractmethod
    async def _processMessage(self, protocolNumber, senderId, content):
        pass
        
    