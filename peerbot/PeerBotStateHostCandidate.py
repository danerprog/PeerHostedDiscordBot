from peerbot.Configuration import CONFIG
from peerbot.PeerBotState import PeerBotState
from peerbot.Signals import SIGNAL
from utils.Logger import Logger

import asyncio

class PeerBotStateHostCandidate(PeerBotState):

    NUMBER_OF_SECONDS_TO_WAIT_FOR_HOST_CANDIDATE_REPLY = 5

    def __init__(self, stateMachine):
        self.logger = Logger.getLogger("PeerBotStateHostCandidate - " + str(stateMachine.getUserId()))
        super().__init__(stateMachine, self.logger)
        
    def start(self):
        self.sendInternalMessageTask = asyncio.ensure_future(self._sendHostCandidateProtocolTimeElapsedSignalAfterAwaitingSleep())
    
    def _processMessage(self, signalNumber, senderId, content):
        if(signalNumber == SIGNAL["HostDeclaration"]):
            self.sendInternalMessageTask.cancel()
            import peerbot.PeerBotStateHostChecking
            self.stateMachine.next(peerbot.PeerBotStateHostChecking.PeerBotStateHostChecking(self.stateMachine))
        elif(signalNumber == SIGNAL["HostCandidateProtocolTimeElapsed"]):
            import peerbot.PeerBotStateRehosting
            self.stateMachine.next(peerbot.PeerBotStateRehosting.PeerBotStateRehosting(self.stateMachine))
        elif(signalNumber == SIGNAL["PriorityNumberDeclaration"]):
            receivedPriorityNumber = int(content)
            asyncio.ensure_future(self._broadcastPriorityNumberDeclarationIfPriorityNumberIsConflicting(receivedPriorityNumber))
            
    async def _sendHostCandidateProtocolTimeElapsedSignalAfterAwaitingSleep(self):
        self.logger.trace("_sendHostCandidateProtocolTimeElapsedSignalAfterAwaitingSleep called")
        await asyncio.sleep(CONFIG["NumberOfSecondsToWaitForHostDeclarationSignal"])
        
        self.logger.trace("_sendHostCandidateProtocolTimeElapsedSignalAfterAwaitingSleep timer expired")
        self._processMessage(SIGNAL["HostCandidateProtocolTimeElapsed"], self.userId, '')
        
        
        