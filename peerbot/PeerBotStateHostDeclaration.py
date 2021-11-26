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
        asyncio.ensure_future(self._broadcastHostDeclarationSignal())
        self.sendInternalMessageTask = asyncio.ensure_future(self._sendHostDeclarationProtocolTimeElapsedSignal())
       
    def _processMessage(self, protocolNumber, senderId, content):
        if(protocolNumber == SIGNAL["RehostingInProgress"]):
            self.sendInternalMessageTask.cancel()
            import peerbot.PeerBotStateAssignPriority
            self.stateMachine.next(peerbot.PeerBotStateAssignPriority.PeerBotStateAssignPriority(self.stateMachine, self.stateMachine.getPriorityNumber() + 1))
        elif(protocolNumber == SIGNAL["HostDeclarationProtocolTimeElapsed"]):
            self.start()
        elif(protocolNumber == SIGNAL["RequestHostDeclarationFromHost"]):
            asyncio.ensure_future(self._broadcastHostDeclarationSignal())
        elif(protocolNumber == SIGNAL["PriorityNumberDeclaration"]):
            receivedPriorityNumber = int(content)
            asyncio.ensure_future(self._broadcastPriorityNumberDeclarationIfPriorityNumberIsConflicting(receivedPriorityNumber))
        elif(protocolNumber == SIGNAL["HostDeclaration"]):
            receivedPriorityNumber = int(content)
            if(receivedPriorityNumber > self.stateMachine.getPriorityNumber()):
                self.logger.trace("receivedPriorityNumber > self.stateMachine.getPriorityNumber(). stepping down as host")
                self.sendInternalMessageTask.cancel()
            
    async def _sendHostDeclarationProtocolTimeElapsedSignal(self):
        self.logger.trace("_sendHostDeclarationProtocolTimeElapsedSignal called")
        await asyncio.sleep(CONFIG["NumberOfSecondsToWaitForHostDeclarationToBeSent"])
        
        self.logger.trace("_sendHostDeclarationProtocolTimeElapsedSignal timer expired")
        self._processMessage(SIGNAL["HostDeclarationProtocolTimeElapsed"], self.userId, '')
        
    async def _broadcastHostDeclarationSignal(self):
        self.numberOfTimesHostDeclarationSignalHasBeenBroadcast += 1
        content = str(self.stateMachine.getPriorityNumber()) + " " + str(self.stateMachine.getRehostCycleId())
        
        sentmessage = await self.stateMachine.getProtocolChannel().send(self._createMessage(SIGNAL["HostDeclaration"], content, self.numberOfTimesHostDeclarationSignalHasBeenBroadcast))
        self.logger.debug(sentmessage.content)
        
    