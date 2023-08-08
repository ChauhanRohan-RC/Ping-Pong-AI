# Ping-Pong Online Multiplayer AI

#### An Online Multiplayer Ping-Pong game with NEAT-AI in python

##### [Demo on Youtube](https://youtu.be/KYO4i3YMgJk)
###### See also 
[3D N*N Rubik's Cube solver-AI](https://github.com/ChauhanRohan-RC/Cube.git)  
[Fourier Series Simulation](https://github.com/ChauhanRohan-RC/Fourier-Series.git)  
[RSA Encryptor](https://github.com/ChauhanRohan-RC/RSA-Encryptor.git)

![Home Screen](graphics/home_screen.png?raw=true)

## Overview
* Four Difficulty levels 
  * Easy
  * Normal 
  * Hard
  * Expert
* Three Playing Modes 
  * Online Multi-Player: Difficulty level based match-marking
  * Offline Multi-Player: Separate controls for both player
  * Offline Single-Player: play against NEAT trained AI
* Create your own server
  * Configurable Server Address and Port 
  * For Local and Remote Settings, see config folder

![Paused](graphics/offline_singleplayer_paused.png?raw=true)

## Clone repository
To clone the repository, run  
`git clone https://github.com/ChauhanRohan-RC/Ping-Pong.git`

## Usage - Server

To start the server, execute  
`python pong_server.py {server_ip} {server_port}`  
  
`server_ip` and `server_port` are optional. Uses default ip and port if not specified

![Online Multiplayer](graphics/online_multiplayer.png?raw=true)

## Usage - Client

* To configure Server Address on the client side, modify  
`config/client_net_config.ini`
* To run the client, execute  
`python pong_client.py {server_ip} {server_port}`  
This command uses `config/client_net_config.ini` as a fallback in case the server address is not specified
* For the client executable (specifically on windows), extract `exe/PingPong.zip` and run `Ping Pong.exe`
* To change the local settings i.e. Player Name, modify `config/local_config.ini`

![Online Multiplayer Result](graphics/online_multiplayer_result.png?raw=true)

## Connect on
[Twitter](https://twitter.com/0rc_studio)  
[Youtube](https://www.youtube.com/channel/UCmyvutGWtyBRva_jrZfyORA)  
[Google Play Store](https://play.google.com/store/apps/dev?id=7315303590538030232)  
E-mail: com.production.rc@gmail.com
