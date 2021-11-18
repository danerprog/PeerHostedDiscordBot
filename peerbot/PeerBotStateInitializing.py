from peerbot.PeerBotState import PeerBotState
from peerbot.PeerBotStateLogin import PeerBotStateLogin
from utils.Logger import Logger

class PeerBotStateInitializing(PeerBotState):
    
    def __init__(self, stateMachine):
        self.logger = Logger.getLogger("PeerBotStateInitializing - " + str(stateMachine.getUserId()))
        super().__init__(stateMachine, self.logger)
        
    async def start(self):
        await self.stateMachine.next(PeerBotStateLogin(self.stateMachine))
        
    async def _processMessage(self, protocolNumber, senderId, content):
        self.logger.warning("Unexpected message found. protocolNumber: " + str(protocolNumber))
        
    