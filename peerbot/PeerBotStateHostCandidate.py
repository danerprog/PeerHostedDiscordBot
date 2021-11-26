from peerbot.PeerBotState import PeerBotState
from utils.Logger import Logger

import asyncio

class PeerBotStateHostCandidate(PeerBotState):

    NUMBER_OF_SECONDS_TO_WAIT_FOR_HOST_CANDIDATE_REPLY = 5

    def __init__(self, stateMachine):
        self.logger = Logger.getLogger("PeerBotStateHostCandidate - " + str(stateMachine.getUserId()))
        super().__init__(stateMachine, self.logger)
        
    def start(self):
        self.sendInternalMessageTask = asyncio.ensure_future(self._send9903AfterTimerExpires())
    
    def _processMessage(self, protocolNumber, senderId, content):
        if(protocolNumber == 202):
            self.sendInternalMessageTask.cancel()
            import peerbot.PeerBotStateHostChecking
            self.stateMachine.next(peerbot.PeerBotStateHostChecking.PeerBotStateHostChecking(self.stateMachine))
        elif(protocolNumber == 9903):
            import peerbot.PeerBotStateRehosting
            self.stateMachine.next(peerbot.PeerBotStateRehosting.PeerBotStateRehosting(self.stateMachine))
        elif(protocolNumber == 301):
            receivedPriorityNumber = int(content)
            asyncio.ensure_future(self._broadcastPriorityNumberDeclarationIfPriorityNumberIsConflicting(receivedPriorityNumber))
            
    async def _send9903AfterTimerExpires(self):
        self.logger.trace("_send9903AfterTimerExpires called")
        await asyncio.sleep(PeerBotStateHostCandidate.NUMBER_OF_SECONDS_TO_WAIT_FOR_HOST_CANDIDATE_REPLY)
        
        self.logger.trace("_send9903AfterTimerExpires timer expired")
        self._processMessage(9903, self.userId, '')
        
        
        