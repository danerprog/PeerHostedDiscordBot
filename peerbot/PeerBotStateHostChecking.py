from peerbot.PeerBotState import PeerBotState
from utils.Logger import Logger

import asyncio

class PeerBotStateHostChecking(PeerBotState):

    NUMBER_OF_SECONDS_TO_WAIT_FOR_HOST_CANDIDATE_REPLY = 5

    def __init__(self, stateMachine, priorityNumber):
        self.logger = Logger.getLogger("PeerBotStateHostChecking - " + str(stateMachine.getUserId()))
        self.priorityNumber = priorityNumber
        self.hostCheckingProtocolInternalMessageId = 0
        super().__init__(stateMachine)
        
    async def start(self):
        await asyncio.sleep(PeerBotStateHostChecking.NUMBER_OF_SECONDS_TO_WAIT_FOR_HOST_CANDIDATE_REPLY)
        await self._processMessage(9901, self.userId, ++self.hostCheckingProtocolInternalMessageId)
    
    async def _processMessage(self, protocolNumber, senderId, content):
        if(protocolNumber == 202):
            await self.start()
        elif(protocolNumber == 206):
            import peerbot.PeerBotStateHostCandidate
            await self.stateMachine.next(peerbot.PeerBotStateHostCandidate.PeerBotStateHostCandidate(self.stateMachine, self.priorityNumber))
        elif(protocolNumber == 9901 and self.hostCheckingProtocolInternalMessageId == int(content)):
            import peerbot.PeerBotStateRehosting
            await self.stateMachine.next(peerbot.PeerBotStateRehosting.PeerBotStateRehosting(self.stateMachine, self.priorityNumber))