from peerbot.Configuration import CONFIG
from peerbot.PeerBotState import PeerBotState
from peerbot.Signals import SIGNAL
from utils.Logger import Logger

import asyncio

class PeerBotStateSynchronize(PeerBotState):

    def __init__(self, stateMachine):
        self.logger = Logger.getLogger("PeerBotStateSynchronize - " + str(stateMachine.getUserId()))
        super().__init__(stateMachine, self.logger)
        
        self.rehostCycleId = 0
        self.priorityNumber = 0
        self.sendInternalMessageTask = None
        
    def start(self):
        self._resetInternalMessageTask()
        
    def _processMessage(self, messageContent):
        signalNumber = messageContent["signalNumber"]
        
        if(signalNumber == SIGNAL["HostDeclaration"]):
            self.priorityNumber = messageContent["content"]["priorityNumber"] + 1
            self.rehostCycleId = messageContent["content"]["rehostCycleId"]
            self._finishSynchronizeProtocol()
        elif(signalNumber == SIGNAL["SynchronizeProtocolTimeElapsed"]):
            self.priorityNumber = 1
            self.rehostCycleId = 1
            self._finishSynchronizeProtocol()
        elif(signalNumber == SIGNAL["RehostingInProgress"]):
            self._resetInternalMessageTask()

    def _finishSynchronizeProtocol(self):
        self.logger.trace("_finishSynchronizeProtocol called")
        
        self.sendInternalMessageTask.cancel()
        self.stateMachine.setRehostCycleId(self.rehostCycleId)
        
        import peerbot.PeerBotStateAssignPriority
        self.stateMachine.next(peerbot.PeerBotStateAssignPriority.PeerBotStateAssignPriority(self.stateMachine, self.priorityNumber))
        
    def _resetInternalMessageTask(self):
        if self.sendInternalMessageTask is not None:
            self.sendInternalMessageTask.cancel()
        self.sendInternalMessageTask = asyncio.ensure_future(self._sendSynchronizeProtocolTimeElapsedSignal())
        
    async def _sendSynchronizeProtocolTimeElapsedSignal(self):
        self.logger.trace("_sendSynchronizeProtocolTimeElapsedSignal called")
        await asyncio.sleep(CONFIG["NumberOfSecondsToWaitForHostDeclarationSignal"])
        
        self.logger.trace("_sendSynchronizeProtocolTimeElapsedSignal timer expired")
        self._processMessage({
            "signalNumber" : SIGNAL["SynchronizeProtocolTimeElapsed"]
        })