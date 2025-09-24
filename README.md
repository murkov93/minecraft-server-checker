# Minecraft Server Status Checker
A minimalist console application to check the status of Minecraft servers, including player count, version information, and server details.

## Features
- Real-time server status checking (online/offline)
- Comprehensive server information display
- Player count and online player list
- Server version and software detection
- Clean, minimalist console interface
- Support for both interactive and command-line modes
- Color-coded output for better readability
- Fallback direct ping if API queries fail

## Information Retrieved
- **Status**: Online/offline status with visual indicators
- **Server Info**: Address, MOTD (Message of the Day), version, software
- **Players**: Current online count, maximum slots, player list (when available)
- **Technical**: Response time (ping), SRV record detection, mod information

## Installation
1. Clone or download the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
### Command Line Mode
```bash
python main.py <server_address>
```
Examples:
```bash
python main.py play.hypixel.net
python main.py "mc.server.com:25566"
```

### Interactive Mode
```bash
python main.py
```
Then enter server addresses when prompted. Type `quit`, `q`, or `exit` to exit the program.
You can also type `examples` to see popular servers to test.

## Requirements
- Python 3.6+
- requests library

## Popular Servers to Test
- `play.hypixel.net` - Hypixel Network
- `mc.mineplex.com` - Mineplex
- `play.cubecraft.net` - CubeCraft Games
- `mineverse.com` - Mineverse
- `cosmicpvp.com` - Cosmic PvP

## API and Technical Details
- Uses mcsrvstat.us API for comprehensive server information
- Falls back to direct TCP ping if API queries fail
- Default port is 25565 if not specified
- Supports custom ports (format: `server:port`)
- Request timeout of 5 seconds for responsive experience

## Example Output
```
============================================================
           Minecraft Server Status Checker
============================================================
Check the status of any Minecraft server

Checking server 'play.hypixel.net:25565'...
   Querying server status...

------------------------------------------------------------

Server Status: ONLINE

SERVER INFORMATION
   Address: play.hypixel.net:25565
   MOTD: Hypixel Network [1.8-1.20] ✦ NEW HOUSING ✦
   Version: Requires MC 1.8 / 1.20

PLAYERS
   Online: 45623/100000
   Player list:
      • Player 1
      • Player 2
      • Player 3
      • Player 
      • ... and .... more

TECHNICAL INFO
   Ping: 45ms
   SRV record: Yes
   Software: BungeeCord 1.19
   Last checked: 14:30:25

------------------------------------------------------------
```

## Error Handling
- Validates server addresses and port numbers
- Handles network timeouts and connection errors
- Provides fallback connectivity checks
- Clear error messages with suggested solutions

## Legal Notice
This tool uses publicly available APIs and standard network protocols to check server status. It respects server rate limits and does not perform any intrusive operations.

## License

This project is open source and available under the MIT License.
