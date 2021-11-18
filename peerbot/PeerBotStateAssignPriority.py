from peerbot.PeerBotState import PeerBotState
from utils.Logger import Logger

import asyncio

class PeerBotStateAssignPriority(PeerBotState):
    
    NUMBER_OF_SECONDS_TO_WAIT_FOR_302 = 3
    
    def __init__(self, stateMachine, priorityNumber):
        self.logger = Logger.getLogger("PeerBotStateAssignPriority - " + str(stateMachine.getUserId()))
        self.priorityNumber = priorityNumber
        super().__init__(stateMachine)
        
    async def start(self):
        sentmessage = await self.stateMachine.getProtocolChannel().send(self._createMessage(301, self.priorityNumber))
        self.logger.debug(sentmessage)
        
        await asyncio.sleep(PeerBotStateAssignPriority.NUMBER_OF_SECONDS_TO_WAIT_FOR_302)
        await self._processMessage(9902, self.userId, '')
        
    async def _processMessage(self, protocolNumber, senderId, content):
        if(protocolNumber == 302):
            ++self.priorityNumber
            self.start()
        elif(protocolNumber == 301):
            if(self.userId > senderId):
                await self._send302IfPriorityNumberIsConflicting(int(content))
        elif(protocolNumber == 9902):
            import peerbot.PeerBotStateHostChecking
            await self.stateMachine.next(peerbot.PeerBotStateHostChecking.PeerBotStateHostChecking(self.stateMachine, self.priorityNumber))
    
    async def _send302IfPriorityNumberIsConflicting(receivedPriorityNumber):
        self.logger.debug("self.priorityNumber: " + str(self.priorityNumber) + ", receivedPriorityNumber: " + str(receivedPriorityNumber))
        if(self.priorityNumber == receivedPriorityNumber):
            self.logger.debug("self.priorityNumber == receivedPriorityNumber")
            await self.stateMachine.getProtocolChannel().send(self._createMessage(302, ''))