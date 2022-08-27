import socket
import R
import U
import C

HOST_NAME = socket.gethostname()
HOST_IP = socket.gethostbyname(HOST_NAME)

# Server
DEFAULT_SERVER_IP = HOST_IP
DEFAULT_SERVER_PORT = 5467
SERVER_TIMEOUT_SECS = 0
SERVER_RECV_BUF_SIZE = 1024

# SERVER_MAX_PLAYERS = 100

FPS_SERVER = R.FPS

# Client
CLIENT_TIMEOUT_SECS = 2
CLIENT_RECV_BUF_SIZE = 1024
FPS_CLIENT = R.FPS


def load_server_addr(file_path: str = R.FILE_PATH_CLIENT_NETWORK_CONFIG,
                     default_ip: str = DEFAULT_SERVER_IP, default_port: int = DEFAULT_SERVER_PORT):
    data = R.load_map(file_path, remove_whitespaces=True)
    ip = data.get(C.NET_CONFIG_KEY_SERVER_IP, "")
    if not (ip and U.is_valid_ip(ip)):
        if ip:
            print(f"Invalid IP in file, IP: {ip}")
        host_name = data.get(C.NET_CONFIG_KEY_SERVER_HOST_NAME, "")
        if host_name:
            try:
                ip = socket.gethostbyname(host_name)
            except Exception:
                ip = default_ip
        else:
            ip = default_ip

    port = default_port
    port_str = data.get(C.NET_CONFIG_KEY_SERVER_PORT)
    if port_str:
        try:
            port = int(port_str)
        except ValueError:
            print(f"Invalid port in file.... PORT: {port_str}")
            port = default_port

    return ip, port
