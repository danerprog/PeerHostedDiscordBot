from peerbot.Signals import SIGNAL

class MessagePacker:

    def __init__(self, logger):
        self.logger = logger
               
    def _packMessage(self, signalNumber, content = '', comments = None):
        self.logger.trace("_packMessage called")
        message = '[' + str(signalNumber) + ' ' + str(self.userId) + ' ' + str(content) + ']'
        if comments != None:
            message += ' ' + str(comments)
        self.logger.debug("Message packed. message: " + message)
        return message
        
    def _packLoginSuccessfulMessage(self):
        self.logger.trace("_packLoginSuccessfulMessage called")
    
        signalNumber = SIGNAL["LoginSuccessful"]
        content = ''
        return self._packMessage(signalNumber, content)
        
    def _packHostDeclarationMessage(self, messageContent):
        self.logger.trace("_packHostDeclarationMessage called")
        
        signalNumber = SIGNAL["HostDeclaration"]
        content = str(messageContent["priorityNumber"]) + " " + str(messageContent["rehostCycleId"])
        comments = self._createCommentsMessageSegmentFromArray(messageContent["comments"])
        return self._packMessage(signalNumber, content, comments)
        
    def _packIntentToBecomeHostDeclarationMessage(self, messageContent):
        self.logger.trace("_packIntentToBecomeHostDeclarationMessage called")
        
        signalNumber = SIGNAL["IntentToBecomeHostDeclaration"]
        content = str(messageContent["priorityNumber"])
        return self._packMessage(signalNumber, content)
        
    def _packRehostingInProgressMessage(self):
        self.logger.trace("_packRehostingInProgressMessage called")
    
        signalNumber = SIGNAL["RehostingInProgress"]
        content = ''
        return self._packMessage(signalNumber, content)
        
    def _packPriorityNumberDeclarationMessage(self, messageContent):
        self.logger.trace("_packPriorityNumberDeclarationMessage called")
        
        signalNumber = SIGNAL["PriorityNumberDeclaration"]
        content = str(messageContent["priorityNumber"])
        return self._packMessage(signalNumber, content)
 
    def _packPriorityNumberIsConflictingMessage(self):
        self.logger.trace("_packLoginSuccessfulMessage called")
        
        signalNumber = SIGNAL["PriorityNumberIsConflicting"]
        content = ''
        return self._packMessage(signalNumber, content)
        
    def _createCommentsMessageSegmentFromArray(self, commentsArray):
        self.logger.trace("_createCommentsMessageSegmentFromArray called")
        
        stringifiedComment = ""
        for comment in commentsArray:
            stringifiedComment += str(comment) + " "
        return stringifiedComment[:-1]