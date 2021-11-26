from peerbot.PeerBotState import PeerBotState
from utils.Logger import Logger

import asyncio

class PeerBotStateAssignPriority(PeerBotState):
    
    NUMBER_OF_SECONDS_TO_WAIT_FOR_302 = 3
    
    def __init__(self, stateMachine, priorityNumber):
        self.logger = Logger.getLogger("PeerBotStateAssignPriority - " + str(stateMachine.getUserId()))
        super().__init__(stateMachine, self.logger)
        self.stateMachine.setPriorityNumber(priorityNumber)
        
    def start(self):
        asyncio.ensure_future(self._broadcast301())
        self.internalMessageTask = asyncio.ensure_future(self._send9902AfterTimerExpires())
        
    def _processMessage(self, protocolNumber, senderId, content):
        if(protocolNumber == 302):
            self.stateMachine.incrementPriorityNumber()
            self.internalMessageTask.cancel()
            self.start()
        elif(protocolNumber == 301):
            receivedPriorityNumber = int(content)
            if(int(self.userId) > int(senderId)):
                asyncio.ensure_future(self._broadcastPriorityNumberDeclarationIfPriorityNumberIsConflicting(receivedPriorityNumber))
        elif(protocolNumber == 9902):
            import peerbot.PeerBotStateHostChecking
            self.stateMachine.next(peerbot.PeerBotStateHostChecking.PeerBotStateHostChecking(self.stateMachine))
            
    async def _send9902AfterTimerExpires(self):
        self.logger.trace("_send9902AfterTimerExpires called")
        await asyncio.sleep(PeerBotStateAssignPriority.NUMBER_OF_SECONDS_TO_WAIT_FOR_302)
        
        self.logger.trace("_send9902AfterTimerExpires timer expired")
        self._processMessage(9902, self.userId, '')
        
    async def _broadcast301(self):
        self.logger.trace("_broadcast301 called")
        sentmessage = await self.stateMachine.getProtocolChannel().send(self._createMessage(301, self.stateMachine.getPriorityNumber()))
        self.logger.debug(sentmessage.content)