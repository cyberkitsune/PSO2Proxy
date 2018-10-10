import commands
import config
import data.clients
import packetFactory
import plugins

login_config = config.YAMLConfig(
    "cfg/loginmessage.config.yml",
    {
        'message': "{{yel}}Welcome to PSO2Proxy build {proxy_ver} "
        "{client_name}! There are currently {client_count} clients "
        "connected. Use {command_prefix}help for a list of commands!",
        'messageType': 0x3
    },
    True
)


@plugins.on_initial_connect_hook
def login_message(sender):
    server_name = "Unknown"
    try:
        import PSO2PDConnector
        server_name = PSO2PDConnector.connector_conf['server_name']
    except ImportError:
        pass
    message = login_config['message'].format(
        client_name=sender.myUsername,
        client_count=len(data.clients.connectedClients),
        proxy_ver=config.proxy_ver,
        command_prefix=config.globalConfig['commandPrefix'],
        server_name=server_name
    )
    sender.send_crypto_packet(packetFactory.SystemMessagePacket(message, login_config['messageType']).build())


@plugins.CommandHook("reloadloginmessage")
class ReloadConfig(commands.Command):
    def call_from_console(self):
        login_config._load_config()
        return "[LoginMessage] Message file reloaded"
