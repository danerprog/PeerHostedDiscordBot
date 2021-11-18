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
        self.setPriorityNumber(0)
        
    async def start(self) :
        self.logger.trace("start called")
        await self.state.start()
        
    async def execute(self, message):
        self.logger.trace("execute called")
        await self.state.execute(message)
        
    def setState(self, state):
        self.logger.trace("setState called")
        self.state = state
        
    async def next(self, state):
        self.logger.debug("next called. state: " + str(state))
        self.setState(state)
        await self.start()
        
    def getUser(self):
        return self.user
        
    def getUserId(self):
        return self.getUser().id
        
    def getProtocolChannel(self):
        return self.protocolChannel
        
    def getPriorityNumber(self):
        return self.priorityNumber
        
    def setPriorityNumber(self, priorityNumber):
        self.priorityNumber = priorityNumber
        
    def incrementPriorityNumber(self):
        self.setPriorityNumber(self.getPriorityNumber() + 1)