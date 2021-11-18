from peerbot.PeerBotState import PeerBotState
from utils.Logger import Logger

import asyncio

class PeerBotStateRehosting(PeerBotState):

    NUMBER_OF_SECONDS_TO_WAIT_FOR_HIGHER_PRIORITY_REHOSTER = 2

    def __init__(self, stateMachine, priorityNumber):
        self.logger = Logger.getLogger("PeerBotStateRehosting - " + str(stateMachine.getUserId()))
        self.priorityNumber = priorityNumber
        self.rehostingProtocolInternalMessageId = 0
        super().__init__(stateMachine)
        
    async def start(self):
        sentmessage = await self.stateMachine.getProtocolChannel().send(self._createMessage(206, ''))
        self.logger.debug(sentmessage)
        
        sentmessage = await self.stateMachine.getProtocolChannel().send(self._createMessage(203, self.priorityNumber))
        self.logger.debug(sentmessage)
        
        await asyncio.sleep(PeerBotStateRehosting.NUMBER_OF_SECONDS_TO_WAIT_FOR_HIGHER_PRIORITY_REHOSTER)
        await self._processMessage(9904, self.userId, ++self.rehostingProtocolInternalMessageId)
    
    async def _processMessage(self, protocolNumber, senderId, content):
        if(protocolNumber == 203):
            priorityNumber = int(content)
            if(self.priorityNumber < priorityNumber):
                import peerbot.PeerBotStateHostChecking
                await self.stateMachine.next(peerbot.PeerBotStateHostChecking.PeerBotStateHostChecking(self.stateMachine, self.priorityNumber))
        elif(protocolNumber == 9904 and self.rehostingProtocolInternalMessageId == int(content)):
            import peerbot.PeerBotStateHostDeclaration
            await self.stateMachine.next(peerbot.PeerBotStateHostDeclaration.PeerBotStateHostDeclaration(self.stateMachine, self.priorityNumber))