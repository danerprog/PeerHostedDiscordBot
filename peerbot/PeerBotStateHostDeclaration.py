from peerbot.Configuration import CONFIG
from peerbot.PeerBotState import PeerBotState
from peerbot.Signals import SIGNAL
from utils.Logger import Logger

import asyncio

class PeerBotStateHostDeclaration(PeerBotState):
    
    def __init__(self, stateMachine):
        self.logger = Logger.getLogger("PeerBotStateHostDeclaration - " + str(stateMachine.getUserId()))
        self.numberOfTimesHostDeclarationSignalHasBeenBroadcast = 0
        super().__init__(stateMachine, self.logger)
        
    def start(self):
        self._broadcastHostDeclarationSignal()
        self.sendInternalMessageTask = asyncio.ensure_future(self._sendHostDeclarationProtocolTimeElapsedSignalAfterAwaitingSleep())
       
    def _processMessage(self, messageContent):
        signalNumber = messageContent["signalNumber"]
        
        if(signalNumber == SIGNAL["RehostingInProgress"]):
            self.sendInternalMessageTask.cancel()
            import peerbot.PeerBotStateAssignPriority
            self.stateMachine.next(peerbot.PeerBotStateAssignPriority.PeerBotStateAssignPriority(self.stateMachine, self.stateMachine.getPriorityNumber() + 1))
        elif(signalNumber == SIGNAL["HostDeclarationProtocolTimeElapsed"]):
            self.start()
        elif(signalNumber == SIGNAL["RequestHostDeclarationFromHost"]):
            self._broadcastHostDeclarationSignal()
        elif(signalNumber == SIGNAL["PriorityNumberDeclaration"]):
            self._broadcastPriorityNumberDeclarationIfPriorityNumberIsConflicting(messageContent["content"]["priorityNumber"])
        elif(signalNumber == SIGNAL["HostDeclaration"]):
            self._stopInternalMessageTaskIfRequired(messageContent["content"]["priorityNumber"])
            
    async def _sendHostDeclarationProtocolTimeElapsedSignalAfterAwaitingSleep(self):
        self.logger.trace("_sendHostDeclarationProtocolTimeElapsedSignalAfterAwaitingSleep called")
        await asyncio.sleep(CONFIG["NumberOfSecondsToWaitForHostDeclarationToBeSent"])
        
        self.logger.trace("_sendHostDeclarationProtocolTimeElapsedSignalAfterAwaitingSleep timer expired")
        self._processMessage({
            "signalNumber" : SIGNAL["HostDeclarationProtocolTimeElapsed"]
        })
        
    def _broadcastHostDeclarationSignal(self):
        self.numberOfTimesHostDeclarationSignalHasBeenBroadcast += 1
        contentDictionary = {
            "priorityNumber" : self.stateMachine.getPriorityNumber(),
            "rehostCycleId" : self.stateMachine.getRehostCycleId(),
            "comments" : [self.numberOfTimesHostDeclarationSignalHasBeenBroadcast]
        }
        message = self._packHostDeclarationMessage(contentDictionary)
        self._sendMessage(message)
        
    def _stopInternalMessageTaskIfRequired(self, receivedPriorityNumber):
        if(receivedPriorityNumber > self.stateMachine.getPriorityNumber()):
            self.logger.trace("messageContent['content']['priorityNumber'] > self.stateMachine.getPriorityNumber(). stepping down as host")
            self.sendInternalMessageTask.cancel()
        
    