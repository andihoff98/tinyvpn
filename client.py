from configuration import Configuration


CONFIG_PATH = "mvpn-client.cfg"

TUN_SET_IFF = 0x400454ca
TUN_SET_OWNER = TUN_SET_IFF + 2
IFF_TUN = 0x0001
IFF_TAP = 0x0002
IFF_NO_PI = 0x1000


class ClientConfiguration(Configuration):

    def __init__(self):
        Configuration.__init__(self)
        self.load(CONFIG_PATH)

    def getServerIp(self):
        return self.get("server_ip", "ip")

    def getServerPort(self):
        return int(self.get("server_port", "8610"))


if __name__ == "__main__":
    clientConfig = ClientConfiguration()
    print("Config:", clientConfig.table)
