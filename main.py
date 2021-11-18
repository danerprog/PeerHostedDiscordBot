from peerbot.PeerBot import PeerBot
from utils.Logger import Logger

import asyncio
import discord
import sys
    
args = {}
args['userId'] = int(sys.argv[1])
args['protocolChannelId'] = int(sys.argv[2])

client = PeerBot(args)
client.run(sys.argv[3])