from colorama import Fore, Style, init
init(autoreset=True)


class DevUI:
    @staticmethod
    def banner(title: str, port: int):
        print(
f"""
{Fore.GREEN}{Style.BRIGHT}✓ Ready{Style.RESET_ALL}  – started TauPy dev server

{Fore.CYAN}{Style.BRIGHT}Server Info{Style.RESET_ALL}
  • App:        {Fore.BLUE}{title}{Fore.WHITE}
  • Mode:       {Fore.GREEN}Development{Fore.WHITE}
  • Frontend:   {Fore.BLUE}http://localhost:{port}{Fore.WHITE}
  • HMR:        {Fore.GREEN}Enabled
"""
        )

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