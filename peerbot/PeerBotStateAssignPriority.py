from peerbot.PeerBotState import PeerBotState
from utils.Logger import Logger

import asyncio

class PeerBotStateAssignPriority(PeerBotState):
    
    NUMBER_OF_SECONDS_TO_WAIT_FOR_302 = 3
    
    def __init__(self, stateMachine, priorityNumber):
        self.logger = Logger.getLogger("PeerBotStateAssignPriority - " + str(stateMachine.getUserId()))
        super().__init__(stateMachine, self.logger)
        self.stateMachine.setPriorityNumber(priorityNumber)
        
    async def start(self):
        sentmessage = await self.stateMachine.getProtocolChannel().send(self._createMessage(301, self.stateMachine.getPriorityNumber()))
        self.logger.debug(sentmessage)
        await self._send9902AfterTimerExpires()
        
    async def _processMessage(self, protocolNumber, senderId, content):
        if(protocolNumber == 302):
            self.stateMachine.incrementPriorityNumber()
            await self.start()
        elif(protocolNumber == 301):
            receivedPriorityNumber = int(content)
            if(int(self.userId) > int(senderId)):
                await self._send302IfPriorityNumberIsConflicting(receivedPriorityNumber)
        elif(protocolNumber == 9902):
            import peerbot.PeerBotStateHostChecking
            await self.stateMachine.next(peerbot.PeerBotStateHostChecking.PeerBotStateHostChecking(self.stateMachine))
            
    async def _send9902AfterTimerExpires(self):
        self.logger.trace("_send9902AfterTimerExpires called")
        await asyncio.sleep(PeerBotStateAssignPriority.NUMBER_OF_SECONDS_TO_WAIT_FOR_302)
        
        self.logger.trace("_send9902AfterTimerExpires timer expired")
        await self._processMessage(9902, self.userId, '')