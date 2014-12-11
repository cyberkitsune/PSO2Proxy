import config
import data.clients
import plugins
import packetFactory
import subprocess

from commands import Command


login_config = config.YAMLConfig("cfg/loginmessage.config.yml", {'message': "{{yel}}Welcome to PSO2Proxy build {proxy_ver} {client_name}! There are currently {client_count} clients connected. Use {command_prefix}help for a list of commands!", 'messageType': 0x3}, True)


@plugins.on_initial_connect_hook
def login_message(sender):
    message = login_config.get_key('message').format(client_name=sender.myUsername, client_count=len(data.clients.connectedClients), proxy_ver=config.proxy_ver, command_prefix=config.globalConfig.get_key('commandPrefix'))
    sender.send_crypto_packet(packetFactory.SystemMessagePacket(message, login_config.get_key('messageType')).build())


@plugins.CommandHook("reloadloginmessage")
class ReloadConfig(Command):
    def call_from_console(self):
        login_config._load_config()
