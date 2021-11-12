from utils.Logger import Logger

import asyncio
import discord
import sys

class IrcProtocol(discord.Client):

    class Mode:
        INITIALIZING = 0
        LOGIN = 1
        POST_LOGIN = 2
        ASSIGN_PRIORITY = 3
        HOST_CHECKING = 4
        HOST_CANDIDATE = 5
        REHOSTING = 6
        HOST = 7
        
    NUMBER_OF_SECONDS_TO_WAIT_FOR_302 = 3
    NUMBER_OF_SECONDS_TO_WAIT_FOR_HOST_CHECKING_REPLY = 3
    NUMBER_OF_SECONDS_TO_WAIT_FOR_HOST_CANDIDATE_REPLY = 5
    NUMBER_OF_SECONDS_TO_WAIT_FOR_HIGHER_PRIORITY_REHOSTER = 2
    NUMBER_OF_SECONDS_TO_WAIT_FOR_HOST_DECLARATION_REPLY = 5

    def __init__(self, args):
        self.userId = args['userId']
        self.protocolChannelId =  args['protocolChannelId']
        self.logger = Logger.getLogger("MyClient - " + str(self.userId))
        self.logger.setOutputFile(str(self.userId) + ".txt")
        self.mode = IrcProtocol.Mode.INITIALIZING
        self.priorityNumber = -1;
        self.hostCheckingProtocolInternalMessageId = 0
        self.hostCandidateProtocolInternalMessageId = 0
        self.rehostingProtocolInternalMessageId = 0
        self.hostDeclarationProtocolInternalMessageId = 0
        super().__init__()

    async def on_ready(self):
        self.protocolChannel = await self.fetch_channel(self.protocolChannelId)
        await self._loginProtocol()
        await self._assignPriorityProtocol(1)
        
    async def on_message(self, message):
        protocolNumber, senderUserId, content, comments = self._unpackMessage(message.content)
        senderUserId = int(senderUserId)
        self.logger.info("protocolNumber: " + protocolNumber + ", senderUserId: " + str(senderUserId) + ", content: " + content + ", comments: " + comments)
        if(senderUserId != self.userId):
            await self._processMessage(protocolNumber, senderUserId, content)
 
    async def _loginProtocol(self):
        user = await self.fetch_user(self.userId)
        sentmessage = await self.protocolChannel.send(self._createMessage(101, str(user)))
        self.mode = IrcProtocol.Mode.LOGIN
        
        self.logger.debug(sentmessage)

    async def _assignPriorityProtocol(self, priorityNumber):
        sentmessage = await self.protocolChannel.send(self._createMessage(301, priorityNumber))
        self.mode = IrcProtocol.Mode.ASSIGN_PRIORITY
        self.priorityNumber = int(priorityNumber)
        
        self.logger.debug(sentmessage)
        
        await asyncio.sleep(IrcProtocol.NUMBER_OF_SECONDS_TO_WAIT_FOR_302)
        await self._processMessage(9902, self.userId, '')
        
    async def _hostCheckingProtocol(self):
        self.mode = IrcProtocol.Mode.HOST_CHECKING
        await asyncio.sleep(IrcProtocol.NUMBER_OF_SECONDS_TO_WAIT_FOR_HOST_CHECKING_REPLY)
        await self._processMessage(9901, self.userId, ++self.hostCheckingProtocolInternalMessageId)
    
    async def _hostCandidateProtocol(self):
        self.mode = IrcProtocol.Mode.HOST_CANDIDATE
        await asyncio.sleep(IrcProtocol.NUMBER_OF_SECONDS_TO_WAIT_FOR_HOST_CANDIDATE_REPLY)
        
    async def _rehostingProtocol(self):
        sentmessage = await self.protocolChannel.send(self._createMessage(206, ''))
        self.logger.debug(sentmessage)
        self.mode = IrcProtocol.Mode.REHOSTING
        
        sentmessage = await self.protocolChannel.send(self._createMessage(203, self.priorityNumber))
        self.logger.debug(sentmessage)
        
        await asyncio.sleep(IrcProtocol.NUMBER_OF_SECONDS_TO_WAIT_FOR_HIGHER_PRIORITY_REHOSTER)
        await self._processMessage(9904, self.userId, ++self.rehostingProtocolInternalMessageId)
        
    async def _hostDeclarationProtocol(self):
        sentmessage = await self.protocolChannel.send(self._createMessage(202, ''))
        self.logger.debug(sentmessage)
        self.mode = IrcProtocol.Mode.HOST
        
        await asyncio.sleep(IrcProtocol.NUMBER_OF_SECONDS_TO_WAIT_FOR_HOST_DECLARATION_REPLY)
        await self._processMessage(9905, self.userId, ++self.hostDeclarationProtocolInternalMessageId)
        
    async def _processMessage(self, protocolNumber, senderId, content):
        if(self.mode == IrcProtocol.Mode.ASSIGN_PRIORITY):
            await self._processAssignPriorityMessage(protocolNumber, senderId, content)
        elif(self.mode == IrcProtocol.Mode.HOST_CHECKING):
            await self._processHostCheckingMessage(protocolNumber, content)
        elif(self.mode == IrcProtocol.Mode.HOST_CANDIDATE):
            await self._processHostCandidateMessage(protocolNumber, content)
        elif(self.mode == IrcProtocol.Mode.REHOSTING):
            await self._processRehostingMessage(protocolNumber, content)
        elif(self.mode == IrcProtocol.Mode.HOST):
            self.logger.debug("self.mode == IrcProtocol.Mode.HOST")
            await self._processHostDeclarationMessage(protocolNumber, content)
            
        if(self.mode > IrcProtocol.Mode.ASSIGN_PRIORITY and protocolNumber == 301):
            self.logger.debug("self.mode > IrcProtocol.Mode.ASSIGN_PRIORITY")
            await self._send302IfPriorityNumberIsConflicting(int(content))

    async def _processAssignPriorityMessage(self, protocolNumber, senderId, content):
        if(protocolNumber == 302):
            priorityNumber = int(content)
            await self._assignPriorityProtocol(priorityNumber + 1)
        elif(protocolNumber == 301):
            if(self.userId > senderId):
                await self._send302IfPriorityNumberIsConflicting(int(content))
        elif(protocolNumber == 9902):
            await self._hostCheckingProtocol()
            
    async def _processHostCheckingMessage(self, protocolNumber, content):
        if(protocolNumber == 202):
            await self._hostCheckingProtocol()
        elif(protocolNumber == 206):
            await self._hostCandidateProtocol()
        elif(protocolNumber == 9901 and self.hostCheckingProtocolInternalMessageId == int(content)):
            await self._rehostingProtocol()
            
    async def _processHostCandidateMessage(self, protocolNumber, content):
        if(protocolNumber == 202):
            await self._hostCheckingProtocol()
        elif(protocolNumber == 9903 and self.hostCandidateProtocolInternalMessageId == int(content)):
            await self._rehostingProtocol()
            
    async def _processRehostingMessage(self, protocolNumber, content):
        if(protocolNumber == 203):
            priorityNumber = int(content)
            if(self.priorityNumber < priorityNumber):
                await self._hostCheckingProtocol()
        elif(protocolNumber == 9904 and self.rehostingProtocolInternalMessageId == int(content)):
            await self._hostDeclarationProtocol()
            
    async def _processHostDeclarationMessage(self, protocolNumber, content):
        if(protocolNumber == 206):
            await self._assignPriorityProtocol(self.priorityNumber + 1)
        elif(protocolNumber == 201 or protocolNumber == 9905 and self.hostDeclarationProtocolInternalMessageId == int(content)):
            await self._hostDeclarationProtocol()
            
    async def _send302IfPriorityNumberIsConflicting(receivedPriorityNumber):
        self.logger.debug("self.priorityNumber: " + str(self.priorityNumber) + ", receivedPriorityNumber: " + str(receivedPriorityNumber))
        if(self.priorityNumber == receivedPriorityNumber):
            self.logger.debug("self.priorityNumber == receivedPriorityNumber")
            await self.protocolChannel.send(self._createMessage(302, ''))
        
    def _createMessage(self, protocolNumber, content = '', comments = None):
        message = '[' + str(protocolNumber) + ' ' + str(self.userId) + ' ' + str(content) + ']'
        if comments != None:
            message += ' ' + str(comments)
        return message
        
    def _unpackMessage(self, message):
        importantMessage, comments = message.split("]", 2)
        protocolNumber, userId, content = importantMessage[1:].split(" ", 3)
        return protocolNumber, userId, content, comments
            
args = {}
args['userId'] = int(sys.argv[1])
args['protocolChannelId'] = int(sys.argv[2])

client = IrcProtocol(args)
client.run('ODg5ODI4NjE0MzQwNzM5MTIy.YUm7eQ.j7mJEEubw0sjrNUI06DjausTYVg')