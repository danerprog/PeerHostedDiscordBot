from peerbot.Configuration import CONFIG
from peerbot.PeerBotState import PeerBotState
from peerbot.Signals import SIGNAL
from utils.Logger import Logger

import asyncio

class PeerBotStateRehosting(PeerBotState):

    NUMBER_OF_SECONDS_TO_WAIT_FOR_HIGHER_PRIORITY_REHOSTER = 2

    def __init__(self, stateMachine):
        self.logger = Logger.getLogger("PeerBotStateRehosting - " + str(stateMachine.getUserId()))
        super().__init__(stateMachine, self.logger)
        
    def start(self):
        asyncio.ensure_future(self._broadcastRehostingInProgressSignal())
        asyncio.ensure_future(self._broadcastIntentToBecomeHostDeclarationSignal())
        self.sendInternalMessageTask = asyncio.ensure_future(self._sendRehostingProtocolTimeElapsedAfterAwaitingSleep())

    def _processMessage(self, signalNumber, senderId, content):
        if(signalNumber == SIGNAL["IntentToBecomeHostDeclaration"]):
            priorityNumber = int(content)
            if(self.stateMachine.getPriorityNumber() < priorityNumber):
                self.logger.trace("self.stateMachine.getPriorityNumber() < priorityNumber")
                self.sendInternalMessageTask.cancel()
                import peerbot.PeerBotStateHostChecking
                self.stateMachine.next(peerbot.PeerBotStateHostChecking.PeerBotStateHostChecking(self.stateMachine))
        elif(signalNumber == SIGNAL["RehostingProtocolTimeElapsed"]):
            import peerbot.PeerBotStateHostDeclaration
            self.stateMachine.next(peerbot.PeerBotStateHostDeclaration.PeerBotStateHostDeclaration(self.stateMachine))
        elif(signalNumber == SIGNAL["PriorityNumberDeclaration"]):
            receivedPriorityNumber = int(content)
            asyncio.ensure_future(self._broadcastPriorityNumberDeclarationIfPriorityNumberIsConflicting(receivedPriorityNumber))
            
    async def _sendRehostingProtocolTimeElapsedAfterAwaitingSleep(self):
        self.logger.trace("_sendRehostingProtocolTimeElapsedAfterAwaitingSleep called")
        await asyncio.sleep(CONFIG["NumberOfSecondsToWaitForAHigherPriorityRehoster"])
        
        self.logger.trace("_sendRehostingProtocolTimeElapsedAfterAwaitingSleep timer expired")
        self._processMessage(SIGNAL["RehostingProtocolTimeElapsed"], self.userId, '')
        
    async def _broadcastRehostingInProgressSignal(self):
        self.logger.trace("_broadcastRehostingInProgressSignal called")
        sentmessage = await self.stateMachine.getProtocolChannel().send(self._createMessage(SIGNAL["RehostingInProgress"], ''))
        self.logger.debug(sentmessage.content)
        
    async def _broadcastIntentToBecomeHostDeclarationSignal(self):
        self.logger.trace("_broadcastIntentToBecomeHostDeclarationSignal called")
        sentmessage = await self.stateMachine.getProtocolChannel().send(self._createMessage(SIGNAL["IntentToBecomeHostDeclaration"], self.stateMachine.getPriorityNumber()))
        self.logger.debug(sentmessage.content)