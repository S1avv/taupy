from colorama import Fore, Style, init
from .reloader import clear_console

import platform
import os
import sys
import psutil

init(autoreset=True)

class DevUI:
    @staticmethod
    def banner(title: str, port: int, ws_port: int = 8765, dev: bool = False):
        clear_console()

        mode_str = f"{Fore.GREEN}Development{Fore.WHITE}" if dev else f"{Fore.GREEN}Production{Fore.WHITE}"
        hmr_str = f"{Fore.GREEN}Enabled{Fore.WHITE}" if dev else f"{Fore.RED}Disabled{Fore.WHITE}"

        print(f"""
    {Fore.GREEN}{Style.BRIGHT}✓ Ready{Style.RESET_ALL} – TauPy dev server started

    {Fore.CYAN}{Style.BRIGHT}Application{Style.RESET_ALL}
    • Name:       {Fore.BLUE}{title}{Fore.WHITE}
    • Mode:       {mode_str}
    • Entrypoint: {sys.argv[0]}
    • CWD:        {os.getcwd()}

    {Fore.CYAN}{Style.BRIGHT}Server{Style.RESET_ALL}
    • Frontend:   http://localhost:{port}
    • WebSocket:  ws://localhost:{ws_port}
    • HMR:        {hmr_str}
    """)

    @staticmethod
    def hmr_trigger(files):
        clean = ", ".join([f.split("\\")[-1] for f in files])
        print(f"{Fore.MAGENTA}{Style.BRIGHT}HMR  {Style.RESET_ALL}reload triggered by {Fore.WHITE}{clean}")

    @staticmethod
    def restart():
        print(f"{Fore.YELLOW}{Style.BRIGHT}Restarting backend...{Style.RESET_ALL}\n")

    @staticmethod
    def connected():
        print(f"{Fore.GREEN}{Style.BRIGHT}✓ WebSocket connected{Style.RESET_ALL}")