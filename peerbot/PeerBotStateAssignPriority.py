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
        asyncio.ensure_future(self._broadcastPriorityNumberDeclarationSignal())
        self.internalMessageTask = asyncio.ensure_future(self._sendAssignPriorityProtocolTimeElapsedSignalAfterAwaitingSleep())
        
    def _processMessage(self, signalNumber, senderId, content):
        if(signalNumber == SIGNAL["PriorityNumberIsConflicting"]):
            self.stateMachine.incrementPriorityNumber()
            self.internalMessageTask.cancel()
            self.start()
        elif(signalNumber == SIGNAL["PriorityNumberDeclaration"]):
            receivedPriorityNumber = int(content)
            if(int(self.userId) > int(senderId)):
                asyncio.ensure_future(self._broadcastPriorityNumberDeclarationIfPriorityNumberIsConflicting(receivedPriorityNumber))
        elif(signalNumber == SIGNAL["AssignPriorityProtocolTimeElapsed"]):
            import peerbot.PeerBotStateHostChecking
            self.stateMachine.next(peerbot.PeerBotStateHostChecking.PeerBotStateHostChecking(self.stateMachine))
            
    async def _sendAssignPriorityProtocolTimeElapsedSignalAfterAwaitingSleep(self):
        self.logger.trace("_sendAssignPriorityProtocolTimeElapsedSignalAfterAwaitingSleep called")
        await asyncio.sleep(CONFIG["NumberOfSecondsToWaitForPriorityNumberIsConflictingSignal"])
        
        self.logger.trace("_sendAssignPriorityProtocolTimeElapsedSignalAfterAwaitingSleep timer expired")
        self._processMessage(SIGNAL["AssignPriorityProtocolTimeElapsed"], self.userId, '')
        
    async def _broadcastPriorityNumberDeclarationSignal(self):
        self.logger.trace("_broadcastPriorityNumberDeclarationSignal called")
        sentmessage = await self.stateMachine.getProtocolChannel().send(self._createMessage(SIGNAL["PriorityNumberDeclaration"], self.stateMachine.getPriorityNumber()))
        self.logger.debug(sentmessage.content)