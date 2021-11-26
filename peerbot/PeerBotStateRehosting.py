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
        self._broadcastRehostingInProgressSignal()
        self._broadcastIntentToBecomeHostDeclarationSignal()
        self.sendInternalMessageTask = asyncio.ensure_future(self._sendRehostingProtocolTimeElapsedAfterAwaitingSleep())

    def _processMessage(self, messageContent):
        signalNumber = messageContent["signalNumber"]
        
        if(signalNumber == SIGNAL["IntentToBecomeHostDeclaration"]):
            self._moveToHostCheckingStateIfAllowed(messageContent["content"]["priorityNumber"])
        elif(signalNumber == SIGNAL["RehostingProtocolTimeElapsed"]):
            import peerbot.PeerBotStateHostDeclaration
            self.stateMachine.next(peerbot.PeerBotStateHostDeclaration.PeerBotStateHostDeclaration(self.stateMachine))
        elif(signalNumber == SIGNAL["PriorityNumberDeclaration"]):
            receivedPriorityNumber = int(content)
            self._broadcastPriorityNumberDeclarationIfPriorityNumberIsConflicting(receivedPriorityNumber)
            
    async def _sendRehostingProtocolTimeElapsedAfterAwaitingSleep(self):
        self.logger.trace("_sendRehostingProtocolTimeElapsedAfterAwaitingSleep called")
        await asyncio.sleep(CONFIG["NumberOfSecondsToWaitForAHigherPriorityRehoster"])
        
        self.logger.trace("_sendRehostingProtocolTimeElapsedAfterAwaitingSleep timer expired")
        self._processMessage({
            "signalNumber" : SIGNAL["RehostingProtocolTimeElapsed"]
        })
        
    def _moveToHostCheckingStateIfAllowed(self, receivedPriorityNumber):
        self.logger.trace("_moveToHostCheckingStateIfAllowed")
        
        if(self.stateMachine.getPriorityNumber() < messageContent["content"]["priorityNumber"]):
            self.logger.trace("self.stateMachine.getPriorityNumber() < priorityNumber")
            self.sendInternalMessageTask.cancel()
            
            import peerbot.PeerBotStateHostChecking
            self.stateMachine.next(peerbot.PeerBotStateHostChecking.PeerBotStateHostChecking(self.stateMachine))
    
    def _broadcastRehostingInProgressSignal(self):
        self.logger.trace("_broadcastRehostingInProgressSignal called")

        message = self._packRehostingInProgressMessage()
        self._sendMessage(message)
        
    def _broadcastIntentToBecomeHostDeclarationSignal(self):
        self.logger.trace("_broadcastIntentToBecomeHostDeclarationSignal called")
        contentDictionary = {
            "priorityNumber" : self.stateMachine.getPriorityNumber()
        }
        message = self._packIntentToBecomeHostDeclarationMessage(contentDictionary)
        self._sendMessage(message)