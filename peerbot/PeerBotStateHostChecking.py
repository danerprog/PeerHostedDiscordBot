from peerbot.PeerBotState import PeerBotState
from utils.Logger import Logger

import asyncio

class PeerBotStateHostChecking(PeerBotState):

    NUMBER_OF_SECONDS_TO_WAIT_FOR_HOST_CANDIDATE_REPLY = 5

    def __init__(self, stateMachine):
        self.logger = Logger.getLogger("PeerBotStateHostChecking - " + str(stateMachine.getUserId()))
        super().__init__(stateMachine, self.logger)
        
    def start(self):
        self.sendInternalMessageTask = asyncio.ensure_future(self._send9901AfterTimerExpires())
        
    def _processMessage(self, protocolNumber, senderId, content):
        if(protocolNumber == 202):
            self.logger.trace("202 received. cancelling current internal message task.")
            self.sendInternalMessageTask.cancel()
            self.start()
        elif(protocolNumber == 206):
            self.sendInternalMessageTask.cancel()
            import peerbot.PeerBotStateHostCandidate
            self.stateMachine.next(peerbot.PeerBotStateHostCandidate.PeerBotStateHostCandidate(self.stateMachine))
        elif(protocolNumber == 9901):
            import peerbot.PeerBotStateRehosting
            self.stateMachine.next(peerbot.PeerBotStateRehosting.PeerBotStateRehosting(self.stateMachine))
        elif(protocolNumber == 301):
            receivedPriorityNumber = int(content)
            asyncio.ensure_future(self._broadcast302IfPriorityNumberIsConflicting(receivedPriorityNumber))
            
    async def _send9901AfterTimerExpires(self):
        self.logger.trace("_send9901AfterTimerExpires called")
        await asyncio.sleep(PeerBotStateHostChecking.NUMBER_OF_SECONDS_TO_WAIT_FOR_HOST_CANDIDATE_REPLY)
        
        self.logger.trace("_send9901AfterTimerExpires timer expired")
        self._processMessage(9901, self.userId, '')