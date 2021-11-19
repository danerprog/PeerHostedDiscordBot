from peerbot.PeerBotState import PeerBotState
from utils.Logger import Logger

import asyncio

class PeerBotStateHostDeclaration(PeerBotState):
    
    NUMBER_OF_SECONDS_TO_WAIT_FOR_HOST_DECLARATION_REPLY = 1
    
    def __init__(self, stateMachine):
        self.logger = Logger.getLogger("PeerBotStateHostDeclaration - " + str(stateMachine.getUserId()))
        self.numberOfTimes202HasBeenBroadcast = 0
        super().__init__(stateMachine, self.logger)
        
    async def start(self):
        await self._broadcast202()
        self.sendInternalMessageTask = asyncio.ensure_future(self._send9905AfterTimerExpires())
       
    async def _processMessage(self, protocolNumber, senderId, content):
        if(protocolNumber == 206):
            self.sendInternalMessageTask.cancel()
            import peerbot.PeerBotStateAssignPriority
            await self.stateMachine.next(peerbot.PeerBotStateAssignPriority.PeerBotStateAssignPriority(self.stateMachine, self.stateMachine.getPriorityNumber() + 1))
        elif(protocolNumber == 9905):
            await self.start()
        elif(protocolNumber == 201):
            await self._broadcast202()
        elif(protocolNumber == 301):
            receivedPriorityNumber = int(content)
            await self._send302IfPriorityNumberIsConflicting(receivedPriorityNumber)
            
    async def _send9905AfterTimerExpires(self):
        self.logger.trace("_send9905AfterTimerExpires called")
        await asyncio.sleep(PeerBotStateHostDeclaration.NUMBER_OF_SECONDS_TO_WAIT_FOR_HOST_DECLARATION_REPLY)
        
        self.logger.trace("_send9905AfterTimerExpires timer expired")
        await self._processMessage(9905, self.userId, '')
        
    async def _broadcast202(self):
        self.numberOfTimes202HasBeenBroadcast += 1
        sentmessage = await self.stateMachine.getProtocolChannel().send(self._createMessage(202, self.numberOfTimes202HasBeenBroadcast))
        self.logger.debug(sentmessage.content)
        
    