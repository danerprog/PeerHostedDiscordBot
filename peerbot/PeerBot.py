from peerbot.PeerBotStateMachine import PeerBotStateMachine
from utils.Logger import Logger

import discord

class PeerBot(discord.Client):
    
    def __init__(self, args):
        self.args = args
        self.isBotReady = False
        super().__init__()
        
    async def on_ready(self):
        stringifiedUserId = str(self.args['userId'])
        self.logger = Logger.getLogger("PeerBot - " + stringifiedUserId)
        self.logger.trace("on_ready called")
        self.stateMachine = PeerBotStateMachine(await self._convertIdToObjects(self.args))
        
        self.isBotReady = True
        await self.stateMachine.start()
        
    async def on_message(self, message):
        if self.isBotReady:
            self.logger.trace("on_message called")
            await self.stateMachine.execute(message)
        
    async def _convertIdToObjects(self, args):
        return {
            'user' : await self.fetch_user(int(args['userId'])),
            'protocolChannel' : await self.fetch_channel(int(args['protocolChannelId']))
        }