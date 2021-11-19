from peerbot.PeerBotState import PeerBotState
from utils.Logger import Logger

import asyncio

class PeerBotStateLogin(PeerBotState):
    
    def __init__(self, stateMachine):
        self.logger = Logger.getLogger("PeerBotStateLogin - " + str(stateMachine.getUserId()))
        super().__init__(stateMachine, self.logger)
        
    def start(self):
        asyncio.ensure_future(self._broadcast101())
        self._goToAssignPriorityState()
        
    def _goToAssignPriorityState(self):
        import peerbot.PeerBotStateAssignPriority
        self.stateMachine.next(peerbot.PeerBotStateAssignPriority.PeerBotStateAssignPriority(self.stateMachine, 1))
        
    def _processMessage(self, protocolNumber, senderId, content):
        self.logger.warning("Unexpected message received. protocolNumber: " + str(protocolNumber) + ", senderId: " + str(senderId) + ", content: " + str(content))
        
    async def _broadcast101(self):
        self.logger.trace("_broadcast101 called")
        user = self.stateMachine.getUser()
        sentmessage = await self.stateMachine.getProtocolChannel().send(self._createMessage(101, str(user.id)))
        self.logger.debug(sentmessage.content)