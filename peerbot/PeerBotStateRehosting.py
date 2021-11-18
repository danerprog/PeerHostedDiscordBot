from peerbot.PeerBotState import PeerBotState
from utils.Logger import Logger

import asyncio

class PeerBotStateRehosting(PeerBotState):

    NUMBER_OF_SECONDS_TO_WAIT_FOR_HIGHER_PRIORITY_REHOSTER = 2

    def __init__(self, stateMachine):
        self.logger = Logger.getLogger("PeerBotStateRehosting - " + str(stateMachine.getUserId()))
        super().__init__(stateMachine, self.logger)
        
    async def start(self):
        sentmessage = await self.stateMachine.getProtocolChannel().send(self._createMessage(206, ''))
        self.logger.debug(sentmessage)
        
        sentmessage = await self.stateMachine.getProtocolChannel().send(self._createMessage(203, self.stateMachine.getPriorityNumber()))
        self.logger.debug(sentmessage)
        
        self.sendInternalMessageTask = asyncio.ensure_future(self._send9904AfterTimerExpires())

    async def _processMessage(self, protocolNumber, senderId, content):
        if(protocolNumber == 203):
            priorityNumber = int(content)
            if(self.stateMachine.getPriorityNumber() < priorityNumber):
                self.logger.trace("self.stateMachine.getPriorityNumber() < priorityNumber")
                self.sendInternalMessageTask.cancel()
                import peerbot.PeerBotStateHostChecking
                await self.stateMachine.next(peerbot.PeerBotStateHostChecking.PeerBotStateHostChecking(self.stateMachine))
        elif(protocolNumber == 9904):
            import peerbot.PeerBotStateHostDeclaration
            await self.stateMachine.next(peerbot.PeerBotStateHostDeclaration.PeerBotStateHostDeclaration(self.stateMachine))
        elif(protocolNumber == 301):
            receivedPriorityNumber = int(content)
            await self._send302IfPriorityNumberIsConflicting(receivedPriorityNumber)
            
    async def _send9904AfterTimerExpires(self):
        await asyncio.sleep(PeerBotStateRehosting.NUMBER_OF_SECONDS_TO_WAIT_FOR_HIGHER_PRIORITY_REHOSTER)
        await self._processMessage(9904, self.userId, '')