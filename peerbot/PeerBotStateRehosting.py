from peerbot.PeerBotState import PeerBotState
from utils.Logger import Logger

import asyncio

class PeerBotStateRehosting(PeerBotState):

    NUMBER_OF_SECONDS_TO_WAIT_FOR_HIGHER_PRIORITY_REHOSTER = 2

    def __init__(self, stateMachine):
        self.logger = Logger.getLogger("PeerBotStateRehosting - " + str(stateMachine.getUserId()))
        super().__init__(stateMachine, self.logger)
        
    def start(self):
        asyncio.ensure_future(self._broadcast206())
        asyncio.ensure_future(self._broadcast203())
        self.sendInternalMessageTask = asyncio.ensure_future(self._send9904AfterTimerExpires())

    def _processMessage(self, signalNumber, senderId, content):
        if(signalNumber == 203):
            priorityNumber = int(content)
            if(self.stateMachine.getPriorityNumber() < priorityNumber):
                self.logger.trace("self.stateMachine.getPriorityNumber() < priorityNumber")
                self.sendInternalMessageTask.cancel()
                import peerbot.PeerBotStateHostChecking
                self.stateMachine.next(peerbot.PeerBotStateHostChecking.PeerBotStateHostChecking(self.stateMachine))
        elif(signalNumber == 9904):
            import peerbot.PeerBotStateHostDeclaration
            self.stateMachine.next(peerbot.PeerBotStateHostDeclaration.PeerBotStateHostDeclaration(self.stateMachine))
        elif(signalNumber == 301):
            receivedPriorityNumber = int(content)
            asyncio.ensure_future(self._broadcastPriorityNumberDeclarationIfPriorityNumberIsConflicting(receivedPriorityNumber))
            
    async def _send9904AfterTimerExpires(self):
        self.logger.trace("_send9904AfterTimerExpires called")
        await asyncio.sleep(PeerBotStateRehosting.NUMBER_OF_SECONDS_TO_WAIT_FOR_HIGHER_PRIORITY_REHOSTER)
        
        self.logger.trace("_send9904AfterTimerExpires timer expired")
        self._processMessage(9904, self.userId, '')
        
    async def _broadcast206(self):
        self.logger.trace("_broadcast206 called")
        sentmessage = await self.stateMachine.getProtocolChannel().send(self._createMessage(206, ''))
        self.logger.debug(sentmessage.content)
        
    async def _broadcast203(self):
        self.logger.trace("_broadcast203 called")
        sentmessage = await self.stateMachine.getProtocolChannel().send(self._createMessage(203, self.stateMachine.getPriorityNumber()))
        self.logger.debug(sentmessage.content)