from peerbot.PeerBotStateLogin import PeerBotStateLogin
from utils.Logger import Logger

import discord

class PeerBotStateMachine:
    def __init__(self, args):
        self.user = args['user']
        self.protocolChannel =  args['protocolChannel']
        self.logger = Logger.getLogger("PeerBotStateMachine - " + str(self.getUser().id))
        super().__init__()
        
        self.state = PeerBotStateLogin(self)
        
    async def start(self) :
        await self.state.start()
        
    async def execute(self, message):
        self.logger.info("Execute called")
        await self.state.execute(message)
        
    def setState(self, state):
        self.logger.info("Setting state")
        self.state = state
        
    async def next(self, state):
        self.setState(state)
        await self.start()
        
    def getUser(self):
        return self.user
        
    def getUserId(self):
        return self.getUser().id
        
    def getProtocolChannel(self):
        return self.protocolChannel