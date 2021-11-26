from abc import ABC
from abc import abstractmethod

class PeerBotState(ABC):

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
            protocolNumber, senderUserIdStr, content, comments = self._unpackMessage(message.content)
            senderUserId = int(senderUserIdStr)
            
            if(self._isMessageFromOwnClient(senderUserId)):
                self.logger.debug("Processing message. protocolNumber: " + protocolNumber + ", senderUserId: " + senderUserIdStr + ", content: " + content)
                self._processMessage(int(protocolNumber), senderUserId, content)

    def _createMessage(self, protocolNumber, content = '', comments = None):
        self.logger.trace("_createMessage called")
        message = '[' + str(protocolNumber) + ' ' + str(self.userId) + ' ' + str(content) + ']'
        if comments != None:
            message += ' ' + str(comments)
        self.logger.debug("Message created. message: " + message)
        return message
        
    def _unpackMessage(self, message):
        self.logger.trace("_unpackMessage called")
        importantMessage, comments = message.split("]", 1)
        protocolNumber, userId, content = importantMessage[1:].split(" ", 2)
        return protocolNumber, userId, content, comments
        
    def _unpackContent(self, protocolNumber, rawContent):
        self.logger.debug("_unpackContent called. protocolNumber: " + str(protocolNumber) + ", rawContent: " + rawContent)
        unpackedContent = {}
        if(protocolNumber == 202):
            tokens = rawContent.split(" ", 2)
            unpackedContent = {
                "priorityNumber" : int(tokens[0]),
                "rehostCycleId" : int(tokens[1])
            }
        else:
            unpackedContent = {
                "content" : rawContent
            }
        return unpackedContent
        
        
    def _isMessageFromOwnClient(self, senderUserId):
        return senderUserId != self.userId
        
    def _isMessageFromOwnAccount(self, message):
        return message.author.id == self.ownId
        
    async def _broadcastPriorityNumberDeclarationIfPriorityNumberIsConflicting(self, receivedPriorityNumber):
        ownPriorityNumber = self.stateMachine.getPriorityNumber()
        self.logger.debug("_broadcastPriorityNumberDeclarationIfPriorityNumberIsConflicting called. ownPriorityNumber: " + str(ownPriorityNumber) + ", receivedPriorityNumber: " + str(receivedPriorityNumber))
        if(ownPriorityNumber == int(receivedPriorityNumber)):
            self.logger.debug("ownPriorityNumber == receivedPriorityNumber")
            await self.stateMachine.getProtocolChannel().send(self._createMessage(302, ''))
        
    @abstractmethod
    async def _processMessage(self, protocolNumber, senderId, content):
        pass
        
    