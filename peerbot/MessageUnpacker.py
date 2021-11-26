from peerbot.Signals import SIGNAL

class MessageUnpacker:

    def __init__(self, logger):
        self.logger = logger

    def _unpackMessage(self, message):
        self.logger.trace("_unpackMessage called")
        protocolMessage, comments = message.split("]", 1)
        rawSignalNumber, userId, rawContent = protocolMessage[1:].split(" ", 2)
        signalNumber = int(rawSignalNumber)
        
        return {
            "signalNumber" : signalNumber,
            "userId" : int(userId),
            "content": self._unpackContent(signalNumber, rawContent),
            "comments": comments
        }
         
    def _unpackContent(self, signalNumber, rawContent):
        self.logger.debug("_unpackContent called. signalNumber: " + str(signalNumber) + ", rawContent: " + rawContent)
        unpackedContent = {}
        
        if(signalNumber == SIGNAL["HostDeclaration"]):
            unpackedContent = self._unpackHostDeclaractionContent(rawContent)
        elif(signalNumber == SIGNAL["IntentToBecomeHostDeclaration"]):
            unpackedContent = self._unpackIntentToBecomeHostDeclarationMessage(rawContent)
        elif(signalNumber == SIGNAL["PriorityNumberDeclaration"]):
            unpackedContent = self._unpackPriorityNumberDeclarationMessage(rawContent)
        else:
            unpackedContent = {
                "content" : rawContent
            }
        return unpackedContent
        
    def _unpackHostDeclaractionContent(self, rawContent):
        tokens = rawContent.split(" ", 2)
        return {
            "priorityNumber" : int(tokens[0]),
            "rehostCycleId" : int(tokens[1])
        }
        
    def _unpackIntentToBecomeHostDeclarationMessage(self, rawContent):
        return {
            "priorityNumber" : int(rawContent)
        }
        
    def _unpackPriorityNumberDeclarationMessage(self, rawContent):
        return {
            "priorityNumber" : int(rawContent)
        }