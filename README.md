.............................................   Ping-Pong   (RC @Aug 9, 2022) .........................................

# An Online Multiplayer Ping-Pong game

1. Offline Single-Player and Multi-Player, Online Multi-Player modes
2. 4 Difficulty levels (Easy, Normal, Hard, Expert)
3. Server Address, Local Settings and many more customisations (see config folder)

# Usage - Server

To start server, execute -> "python pong_server.py {server_ip} {server_port}". Uses default ip and port if not specified

# Usage - Client

1. To specify Server Address on client side, modify "config/client_net_config.ini"
2. Client (on windows), extract "exe/PingPong.zip" and run "Ping Pong.exe"
3. Client (using python), execute -> " python pong_client.py {server_ip} {server_port}". Uses "config/client_net_config.ini" if server address is not specified
4. To change local settings (like player name), modify "config/local_config.ini"

# Support

E-mail: com.production.rc@gmail.com
