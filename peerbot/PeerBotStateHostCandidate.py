from peerbot.PeerBotState import PeerBotState
from utils.Logger import Logger

import asyncio

class PeerBotStateHostCandidate(PeerBotState):

    NUMBER_OF_SECONDS_TO_WAIT_FOR_HOST_CANDIDATE_REPLY = 5

    def __init__(self, stateMachine):
        self.logger = Logger.getLogger("PeerBotStateHostCandidate - " + str(stateMachine.getUserId()))
        super().__init__(stateMachine, self.logger)
        
    async def start(self):
        self.sendInternalMessageTask = asyncio.ensure_future(self._send9903AfterTimerExpires())
    
    async def _processMessage(self, protocolNumber, senderId, content):
        if(protocolNumber == 202):
            self.sendInternalMessageTask.cancel()
            import peerbot.PeerBotStateHostChecking
            await self.stateMachine.next(peerbot.PeerBotStateHostChecking.PeerBotStateHostChecking(self.stateMachine))
        elif(protocolNumber == 9903):
            import peerbot.PeerBotStateRehosting
            await self.stateMachine.next(peerbot.PeerBotStateRehosting.PeerBotStateRehosting(self.stateMachine))
        elif(protocolNumber == 301):
            receivedPriorityNumber = int(content)
            await self._send302IfPriorityNumberIsConflicting(receivedPriorityNumber)
            
    async def _send9903AfterTimerExpires(self):
        await asyncio.sleep(PeerBotStateHostCandidate.NUMBER_OF_SECONDS_TO_WAIT_FOR_HOST_CANDIDATE_REPLY)
        await self._processMessage(9903, self.userId, '')