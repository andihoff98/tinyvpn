from configuration import Configuration
import SocketServer
import socket
import struct
import fcntl
import subprocess


CONFIG_PATH = "mvpn-server.cfg"

TUN_DEVICE = "/dev/net/tun"
TUN_SET_IFF = 0x400454ca
TUN_SET_OWNER = TUN_SET_IFF + 2
IFF_TUN = 0x0001
IFF_TAP = 0x0002
IFF_NO_PI = 0x1000


class ServerConfiguration(Configuration):

    def __init__(self):
        Configuration.__init__(self)
        self.load(CONFIG_PATH)

    def getPublicIp(self):
        return self.get("public_ip", "0.0.0.0")

    def getServerIp(self):
        return self.get("server_ip", "10.0.0.1/24")

    def getPort(self):
        return int(self.get("port", "8610"))

    def getDeviceName(self):
        return self.get("device_name", "mvpn%d")


class ExternalClientHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(65535)


class InternalClientHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        pass


class VPNServer(SocketServer.BaseServer):

    address_family = socket.AF_UNIX
    socket_type = socket.SOCK_DGRAM
    # allow_reuse_address = False

    def __init__(self, dev_name, vpn_ip):
        SocketServer.BaseServer.__init__(self, TUN_DEVICE, InternalClientHandler)
        self.dev_name = dev_name
        self.vpn_ip = vpn_ip
        self.socket = socket.socket(self.address_family, self.socket_type)
        try:
            self.server_bind()
        except:
            self.server_close()
            raise

    def server_bind(self):
        self.socket.bind(TUN_DEVICE)
        ifr = struct.pack("16sH", self.dev_name, IFF_TAP | IFF_NO_PI)
        ifs = fcntl.ioctl(self.socket.fileno(), TUN_SET_IFF, ifr)
        fcntl.ioctl(self.socket.fileno(), TUN_SET_OWNER, 1000)
        self.dev_name = ifs[:16].strip("\x00")
        subprocess.check_call("ifconfig " + self.dev_name + " " + self.vpn_ip, shell=True)

    def get_request(self):
        raw = self.socket.recvfrom(65535)
        return raw[6:12], raw[:6], raw[12:14], raw[14:]  # dst, src, type, data

    def server_close(self):
        self.socket.close()

    def fileno(self):
        return self.socket.fileno()

    def get_device_name(self):
        return self.dev_name


if __name__ == "__main__":
    server_config = ServerConfiguration()
    print("Config:", server_config.table)
    public_host = server_config.getPublicIp()
    public_port = server_config.getPort()
    udp_server = SocketServer.ThreadingUDPServer((public_host, public_port), ExternalClientHandler)
    vpn_server = VPNServer(server_config.getDeviceName())
    try:
        udp_server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down...")
        udp_server.server_close()
