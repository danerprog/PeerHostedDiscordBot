from peerbot.Configuration import CONFIG
from peerbot.PeerBotState import PeerBotState
from peerbot.Signals import SIGNAL
from utils.Logger import Logger

import asyncio

class PeerBotStateHostChecking(PeerBotState):

    def __init__(self, stateMachine):
        self.logger = Logger.getLogger("PeerBotStateHostChecking - " + str(stateMachine.getUserId()))
        super().__init__(stateMachine, self.logger)
        
    def start(self):
        self.sendInternalMessageTask = asyncio.ensure_future(self._sendHostCheckingProtocolTimeElapsedSignalAfterAwaitingSleep())
        
    def _processMessage(self, messageContent):
        signalNumber = messageContent["signalNumber"]
    
        if(signalNumber == SIGNAL["HostDeclaration"]):
            self.logger.trace("host declaration signal received. cancelling current internal message task.")
            self.sendInternalMessageTask.cancel()
            self.start()
        elif(signalNumber == SIGNAL["RehostingInProgress"]):
            self.sendInternalMessageTask.cancel()
            import peerbot.PeerBotStateHostCandidate
            self.stateMachine.next(peerbot.PeerBotStateHostCandidate.PeerBotStateHostCandidate(self.stateMachine))
        elif(signalNumber == SIGNAL["HostCheckingProtocolTimeElapsed"]):
            import peerbot.PeerBotStateRehosting
            self.stateMachine.next(peerbot.PeerBotStateRehosting.PeerBotStateRehosting(self.stateMachine))
        elif(signalNumber == SIGNAL["PriorityNumberDeclaration"]):
            self._broadcastPriorityNumberDeclarationIfPriorityNumberIsConflicting(messageContent["content"]["priorityNumber"])
            
    async def _sendHostCheckingProtocolTimeElapsedSignalAfterAwaitingSleep(self):
        self.logger.trace("_sendHostCheckingProtocolTimeElapsedSignalAfterAwaitingSleep called")
        await asyncio.sleep(CONFIG["NumberOfSecondsToWaitForHostDeclarationSignal"])
        
        self.logger.trace("_sendHostCheckingProtocolTimeElapsedSignalAfterAwaitingSleep timer expired")
        self._processMessage({
            "signalNumber" : SIGNAL["HostCheckingProtocolTimeElapsed"]
        })