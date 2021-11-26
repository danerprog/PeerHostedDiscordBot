from peerbot.PeerBotState import PeerBotState
from peerbot.Signals import SIGNAL
from utils.Logger import Logger

import asyncio

class PeerBotStateLogin(PeerBotState):
    
    def __init__(self, stateMachine):
        self.logger = Logger.getLogger("PeerBotStateLogin - " + str(stateMachine.getUserId()))
        super().__init__(stateMachine, self.logger)
        
    def start(self):
        self._broadcastLoginSuccessfulSignal()
        self._goToAssignPriorityState()
        
    def _goToAssignPriorityState(self):
        import peerbot.PeerBotStateSynchronize
        self.stateMachine.next(peerbot.PeerBotStateSynchronize.PeerBotStateSynchronize(self.stateMachine))
        
    def _processMessage(self, messageContent):
        pass
        
    def _broadcastLoginSuccessfulSignal(self):
        self.logger.trace("_broadcastLoginSuccessfulSignal called")
        
        message = self._packLoginSuccessfulMessage()
        self._sendMessage(message)