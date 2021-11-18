from peerbot.PeerBotState import PeerBotState
from utils.Logger import Logger

import asyncio

class PeerBotStateHostDeclaration(PeerBotState):
    
    NUMBER_OF_SECONDS_TO_WAIT_FOR_HOST_DECLARATION_REPLY = 5
    
    def __init__(self, stateMachine, priorityNumber):
        self.logger = Logger.getLogger("PeerBotStateHostDeclaration - " + str(stateMachine.getUserId()))
        self.hostDeclarationProtocolInternalMessageId = 0
        self.priorityNumber = priorityNumber
        super().__init__(stateMachine)
        
    async def start(self):
        self.logger.info("Starting")
        
        sentmessage = await self.stateMachine.getProtocolChannel().send(self._createMessage(202, ''))
        self.logger.debug(sentmessage)

        await asyncio.sleep(PeerBotStateHostDeclaration.NUMBER_OF_SECONDS_TO_WAIT_FOR_HOST_DECLARATION_REPLY)
        await self._processMessage(9905, self.userId, ++self.hostDeclarationProtocolInternalMessageId)
   
    async def _processMessage(self, protocolNumber, senderId, content):
        if(protocolNumber == 206):
            import peerbot.PeerBotStateAssignPriority
            await self.stateMachine.next(peerbot.PeerBotStateAssignPriority.PeerBotStateAssignPriority(self.stateMachine, self.priorityNumber + 1))
        elif(protocolNumber == 201 or protocolNumber == 9905 and self.hostDeclarationProtocolInternalMessageId == int(content)):
            await self.start()
        
    