from peerbot.PeerBotState import PeerBotState
from peerbot.Signals import SIGNAL
from utils.Logger import Logger

import asyncio

class PeerBotStateLogin(PeerBotState):
    
    def __init__(self, stateMachine):
        self.logger = Logger.getLogger("PeerBotStateLogin - " + str(stateMachine.getUserId()))
        super().__init__(stateMachine, self.logger)
        
    def start(self):
        asyncio.ensure_future(self._broadcastLoginSuccessfulSignal())
        self._goToAssignPriorityState()
        
    def _goToAssignPriorityState(self):
        import peerbot.PeerBotStateSynchronize
        self.stateMachine.next(peerbot.PeerBotStateSynchronize.PeerBotStateSynchronize(self.stateMachine))
        
    def _processMessage(self, signalNumber, senderId, content):
        self.logger.info("Unexpected message received. signalNumber: " + str(signalNumber) + ", senderId: " + str(senderId) + ", content: " + str(content))
        
    async def _broadcastLoginSuccessfulSignal(self):
        self.logger.trace("_broadcastLoginSuccessfulSignal called")
        user = self.stateMachine.getUser()
        sentmessage = await self.stateMachine.getProtocolChannel().send(self._createMessage(SIGNAL["LoginSuccessful"], str(user.id)))
        self.logger.debug(sentmessage.content)