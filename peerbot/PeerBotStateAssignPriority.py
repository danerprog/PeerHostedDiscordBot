from peerbot.Configuration import CONFIG
from peerbot.PeerBotState import PeerBotState
from peerbot.Signals import SIGNAL
from utils.Logger import Logger

import asyncio

class PeerBotStateAssignPriority(PeerBotState):
    
    def __init__(self, stateMachine, priorityNumber):
        self.logger = Logger.getLogger("PeerBotStateAssignPriority - " + str(stateMachine.getUserId()))
        super().__init__(stateMachine, self.logger)
        self.stateMachine.setPriorityNumber(priorityNumber)
        
    def start(self):
        self._broadcastPriorityNumberDeclarationSignal()
        self.internalMessageTask = asyncio.ensure_future(self._sendAssignPriorityProtocolTimeElapsedSignalAfterAwaitingSleep())
        
    def _processMessage(self, messageContent):
        signalNumber = messageContent["signalNumber"]
        
        if(signalNumber == SIGNAL["PriorityNumberIsConflicting"]):
            self.stateMachine.incrementPriorityNumber()
            self.internalMessageTask.cancel()
            self.start()
        elif(signalNumber == SIGNAL["PriorityNumberDeclaration"]):
            if(int(self.userId) > messageContent["userId"]):
                self._broadcastPriorityNumberDeclarationIfPriorityNumberIsConflicting(messageContent["content"]["priorityNumber"])
        elif(signalNumber == SIGNAL["AssignPriorityProtocolTimeElapsed"]):
            import peerbot.PeerBotStateHostChecking
            self.stateMachine.next(peerbot.PeerBotStateHostChecking.PeerBotStateHostChecking(self.stateMachine))
            
    async def _sendAssignPriorityProtocolTimeElapsedSignalAfterAwaitingSleep(self):
        self.logger.trace("_sendAssignPriorityProtocolTimeElapsedSignalAfterAwaitingSleep called")
        await asyncio.sleep(CONFIG["NumberOfSecondsToWaitForPriorityNumberIsConflictingSignal"])
        
        self.logger.trace("_sendAssignPriorityProtocolTimeElapsedSignalAfterAwaitingSleep timer expired")
        self._processMessage({
            "signalNumber" : SIGNAL["AssignPriorityProtocolTimeElapsed"]
        })
        
    def _broadcastPriorityNumberDeclarationSignal(self):
        self.logger.trace("_broadcastPriorityNumberDeclarationSignal called")
        contentDictionary = {
            "priorityNumber" : self.stateMachine.getPriorityNumber()
        }
        message = self._packPriorityNumberDeclarationMessage(contentDictionary)
        self._sendMessage(message)