import requests
import sys
import json
import socket
import struct
import time
from datetime import datetime

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    GRAY = '\033[90m'
    PURPLE = '\033[95m'

class MinecraftServerChecker:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'Minecraft-Server-Checker/1.0'
        })
        self.timeout = 5

    def print_header(self):
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
        print(f"           Minecraft Server Status Checker")
        print(f"{'='*60}{Colors.END}\n")
        print(f"{Colors.GRAY}Check the status of any Minecraft server{Colors.END}\n")

    def print_separator(self):
        print(f"{Colors.GRAY}{'-'*60}{Colors.END}")

    def validate_server_address(self, address):
        """Validate server address format"""
        if not address or not address.strip():
            return False, "Server address cannot be empty"
        
        address = address.strip()
        if len(address) < 3:
            return False, "Server address too short"
        
        # Basic validation for domain/IP format
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_')
        if not all(c in allowed_chars for c in address):
            return False, "Invalid characters in server address"
        
        return True, address

    def validate_port(self, port_str):
        """Validate port number"""
        try:
            port = int(port_str) if port_str else 25565
            if 1 <= port <= 65535:
                return True, port
            else:
                return False, "Port must be between 1 and 65535"
        except ValueError:
            return False, "Port must be a valid number"

    def get_server_status_api(self, server, port):
        """Get server status using mcsrvstat.us API"""
        try:
            url = f"https://api.mcsrvstat.us/3/{server}:{port}"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json(), None
            else:
                return None, f"API error: HTTP {response.status_code}"
                
        except requests.Timeout:
            return None, "Request timeout - server may be slow to respond"
        except requests.RequestException as e:
            return None, f"Network error: {str(e)}"

    def ping_server_direct(self, server, port):
        """Direct ping to Minecraft server using socket"""
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            result = sock.connect_ex((server, port))
            ping_time = round((time.time() - start_time) * 1000, 2)
            
            sock.close()
            
            if result == 0:
                return True, ping_time
            else:
                return False, None
                
        except socket.gaierror:
            return False, None
        except Exception:
            return False, None

    def format_motd(self, motd_data):
        """Format MOTD (Message of the Day)"""
        if not motd_data:
            return "No MOTD"
        
        if isinstance(motd_data, dict):
            if 'clean' in motd_data and motd_data['clean']:
                return ' '.join(motd_data['clean']).strip()
            elif 'raw' in motd_data and motd_data['raw']:
                return ' '.join(motd_data['raw']).strip()
        elif isinstance(motd_data, list):
            return ' '.join(motd_data).strip()
        elif isinstance(motd_data, str):
            return motd_data.strip()
        
        return "No MOTD"

    def format_version(self, version_data):
        """Format version information"""
        if not version_data:
            return "Unknown"
        
        if isinstance(version_data, str):
            return version_data
        elif isinstance(version_data, dict):
            return version_data.get('name', 'Unknown')
        
        return str(version_data)

    def display_server_info(self, server, port, status_data, direct_ping=None):
        """Display comprehensive server information"""
        if not status_data or not status_data.get('online', False):
            print(f"{Colors.BOLD}{Colors.RED}Server Status: OFFLINE{Colors.END}\n")
            
            # Try direct ping if API says offline
            if direct_ping is None:
                is_reachable, ping_time = self.ping_server_direct(server, port)
                if is_reachable:
                    print(f"{Colors.YELLOW}Note: Server port is reachable but may not respond to queries{Colors.END}")
                    print(f"   {Colors.CYAN}Direct ping:{Colors.END} {ping_time}ms")
            
            print(f"\n{Colors.GRAY}Server: {server}:{port}{Colors.END}")
            print(f"{Colors.GRAY}Status checked at: {datetime.now().strftime('%H:%M:%S')}{Colors.END}\n")
            return

        print(f"{Colors.BOLD}{Colors.GREEN}Server Status: ONLINE{Colors.END}\n")
        
        # Basic Information
        print(f"{Colors.BOLD}SERVER INFORMATION{Colors.END}")
        print(f"   {Colors.CYAN}Address:{Colors.END} {server}:{port}")
        
        motd = self.format_motd(status_data.get('motd'))
        if motd and motd != "No MOTD":
            # Limit MOTD length for better display
            if len(motd) > 80:
                motd = motd[:77] + "..."
            print(f"   {Colors.CYAN}MOTD:{Colors.END} {motd}")
        
        version = self.format_version(status_data.get('version'))
        print(f"   {Colors.CYAN}Version:{Colors.END} {version}")
        
        print()
        
        # Player Information
        players_data = status_data.get('players', {})
        if players_data:
            print(f"{Colors.BOLD}PLAYERS{Colors.END}")
            online = players_data.get('online', 0)
            max_players = players_data.get('max', 0)
            print(f"   {Colors.CYAN}Online:{Colors.END} {online}/{max_players}")
            
            if online > 0 and 'list' in players_data and players_data['list']:
                print(f"   {Colors.CYAN}Player list:{Colors.END}")
                for i, player in enumerate(players_data['list'][:10]):  # Show max 10 players
                    player_name = player.get('name', player) if isinstance(player, dict) else player
                    print(f"      • {player_name}")
                
                if len(players_data['list']) > 10:
                    print(f"      {Colors.GRAY}... and {len(players_data['list']) - 10} more{Colors.END}")
            
            print()
        
        # Technical Information
        print(f"{Colors.BOLD}TECHNICAL INFO{Colors.END}")
        
        if 'debug' in status_data and status_data['debug']:
            debug = status_data['debug']
            if 'ping' in debug:
                print(f"   {Colors.CYAN}Ping:{Colors.END} {debug['ping']}ms")
            if 'srv' in debug and debug['srv']:
                print(f"   {Colors.CYAN}SRV record:{Colors.END} Yes")
        else:
            # Fallback to direct ping if no debug info
            is_reachable, ping_time = self.ping_server_direct(server, port)
            if is_reachable and ping_time:
                print(f"   {Colors.CYAN}Direct ping:{Colors.END} {ping_time}ms")
        
        # Software/Mod information
        if 'software' in status_data and status_data['software']:
            print(f"   {Colors.CYAN}Software:{Colors.END} {status_data['software']}")
        
        if 'mods' in status_data and status_data['mods']:
            mod_list = status_data['mods']
            if isinstance(mod_list, list) and mod_list:
                print(f"   {Colors.CYAN}Mods:{Colors.END} {len(mod_list)} detected")
        
        print(f"   {Colors.CYAN}Last checked:{Colors.END} {datetime.now().strftime('%H:%M:%S')}")
        
        print()
        self.print_separator()
        print()

    def check_server(self, server_input):
        """Main function to check server status"""
        if not server_input or not server_input.strip():
            print(f"{Colors.RED}Server address required{Colors.END}\n")
            return False
        
        # Parse server and port
        server_input = server_input.strip()
        if ':' in server_input:
            parts = server_input.rsplit(':', 1)
            server = parts[0]
            port_str = parts[1]
        else:
            server = server_input
            port_str = "25565"
        
        # Validate inputs
        is_valid, server = self.validate_server_address(server)
        if not is_valid:
            print(f"{Colors.RED}Error: {server}{Colors.END}\n")
            return False
        
        is_valid, port = self.validate_port(port_str)
        if not is_valid:
            print(f"{Colors.RED}Error: {port}{Colors.END}\n")
            return False
        
        print(f"{Colors.YELLOW}Checking server '{server}:{port}'...{Colors.END}\n")
        
        print(f"{Colors.GRAY}   Querying server status...{Colors.END}")
        status_data, error = self.get_server_status_api(server, port)
        
        if error:
            print(f"{Colors.RED}API Error: {error}{Colors.END}")
            print(f"{Colors.GRAY}   Trying direct connection...{Colors.END}")
            is_reachable, ping_time = self.ping_server_direct(server, port)
            
            if is_reachable:
                print(f"\n{Colors.YELLOW}Server is reachable but doesn't respond to status queries{Colors.END}")
                print(f"{Colors.CYAN}Direct ping:{Colors.END} {ping_time}ms")
                print(f"{Colors.GRAY}This may be a server with query disabled{Colors.END}\n")
            else:
                print(f"\n{Colors.RED}Server is not reachable{Colors.END}")
                print(f"{Colors.GRAY}Server: {server}:{port}{Colors.END}\n")
            
            return False
        
        print()
        self.print_separator()
        print()
        
        self.display_server_info(server, port, status_data)
        return True

    def show_examples(self):
        """Show example servers"""
        print(f"{Colors.BOLD}Popular Minecraft servers to try:{Colors.END}")
        print(f"   {Colors.CYAN}• play.hypixel.net{Colors.END} - Hypixel Network")
        print(f"   {Colors.CYAN}• mc.mineplex.com{Colors.END} - Mineplex")
        print(f"   {Colors.CYAN}• play.cubecraft.net{Colors.END} - CubeCraft Games")
        print(f"   {Colors.CYAN}• mineverse.com{Colors.END} - Mineverse")
        print(f"   {Colors.CYAN}• cosmicpvp.com{Colors.END} - Cosmic PvP")
        print()

    def run_interactive(self):
        """Run in interactive mode"""
        self.print_header()
        
        while True:
            try:
                server_input = input(f"{Colors.BOLD}Server address{Colors.END} (or 'examples'/'quit'): ")
                
                if server_input.lower() in ['quit', 'q', 'exit']:
                    print(f"\n{Colors.CYAN}Goodbye!{Colors.END}\n")
                    break
                
                if server_input.lower() in ['examples', 'ex', 'help']:
                    print()
                    self.show_examples()
                    continue
                
                print()
                success = self.check_server(server_input)
                
                if success:
                    continue_check = input(f"{Colors.GRAY}Check another server? (y/n): {Colors.END}")
                    if continue_check.lower() not in ['o', 'oui', 'y', 'yes', '']:
                        print(f"\n{Colors.CYAN}Goodbye!{Colors.END}\n")
                        break
                
                print()
                
            except KeyboardInterrupt:
                print(f"\n\n{Colors.CYAN}Goodbye!{Colors.END}\n")
                break
            except EOFError:
                print(f"\n\n{Colors.CYAN}Goodbye!{Colors.END}\n")
                break

    def run_single(self, server_input):
        self.print_header()
        self.check_server(server_input)

def main():
    checker = MinecraftServerChecker()
    
    if len(sys.argv) > 1:
        server_input = sys.argv[1]
        checker.run_single(server_input)
    else:
        checker.run_interactive()

if __name__ == "__main__":
    main()