from abc import ABC
from abc import abstractmethod

class PeerBotState(ABC):

    def __init__(self, stateMachine):
        self.stateMachine = stateMachine    
        self.userId = self.stateMachine.getUser().id
        
    @abstractmethod
    async def start(self):
        pass
        
    async def execute(self, message):
        protocolNumber, senderUserId, content, comments = self._unpackMessage(message.content)
        if(int(senderUserId) != self.userId):
            await self._processMessage(protocolNumber, senderUserId, content)

    def _createMessage(self, protocolNumber, content = '', comments = None):
        message = '[' + str(protocolNumber) + ' ' + str(self.userId) + ' ' + str(content) + ']'
        if comments != None:
            message += ' ' + str(comments)
        return message
        
    def _unpackMessage(self, message):
        importantMessage, comments = message.split("]", 2)
        protocolNumber, userId, content = importantMessage[1:].split(" ", 3)
        return protocolNumber, userId, content, comments
        
    @abstractmethod
    async def _processMessage(self, protocolNumber, senderId, content):
        pass
        
    