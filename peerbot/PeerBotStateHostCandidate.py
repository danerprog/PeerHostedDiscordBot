from peerbot.PeerBotState import PeerBotState
from utils.Logger import Logger

import asyncio

class PeerBotStateHostCandidate(PeerBotState):

    NUMBER_OF_SECONDS_TO_WAIT_FOR_HOST_CANDIDATE_REPLY = 5

    def __init__(self, stateMachine, priorityNumber):
        self.logger = Logger.getLogger("PeerBotStateHostCandidate - " + str(stateMachine.getUserId()))
        self.priorityNumber = priorityNumber
        self.hostCandidateProtocolInternalMessageId = 0
        super().__init__(stateMachine)
        
    async def start(self):
        await asyncio.sleep(IrcProtocol.NUMBER_OF_SECONDS_TO_WAIT_FOR_HOST_CANDIDATE_REPLY)
        await self._processMessage(9903, self.userId, ++self.hostCandidateProtocolInternalMessageId)
    
    async def _processMessage(self, protocolNumber, senderId, content):
        if(protocolNumber == 202):
            import peerbot.PeerBotStateHostChecking
            await self.stateMachine.next(peerbot.PeerBotStateHostChecking.PeerBotStateHostChecking(self.stateMachine, self.priorityNumber))
        elif(protocolNumber == 9903 and self.hostCandidateProtocolInternalMessageId == int(content)):
            import peerbot.PeerBotStateRehosting
            await self.stateMachine.next(peerbot.PeerBotStateRehosting.PeerBotStateRehosting(self.stateMachine, self.priorityNumber))