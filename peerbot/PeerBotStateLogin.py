from peerbot.PeerBotState import PeerBotState
from utils.Logger import Logger

class PeerBotStateLogin(PeerBotState):
    
    def __init__(self, stateMachine):
        self.logger = Logger.getLogger("PeerBotStateLogin - " + str(stateMachine.getUserId()))
        super().__init__(stateMachine)
        
    async def start(self):
        self.logger.info("Starting")
        user = self.stateMachine.getUser()
        sentmessage = await self.stateMachine.getProtocolChannel().send(self._createMessage(101, str(user.id)))
        self.logger.debug(sentmessage)
        
        import peerbot.PeerBotStateAssignPriority
        await self.stateMachine.next(peerbot.PeerBotStateAssignPriority.PeerBotStateAssignPriority(self.stateMachine, 1))
        
    async def _processMessage(self, protocolNumber, senderId, content):
        self.logger.warning("Unexpected message found. protocolNumber: " + str(protocolNumber))
        
    