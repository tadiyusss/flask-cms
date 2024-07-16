from colorama import Fore, Style
import datetime


class Logging:
    def __init__(self, log_file = 'logs'):
        self.info = Fore.BLUE 
        self.error = Fore.RED
        self.success = Fore.GREEN
        self.warning = Fore.YELLOW
        self.log_file = open(f"{log_file}.log", "a")
    def log(self, message, type):
        if type == "info":
            print(f"{self.info}[{datetime.datetime.now()}] [INFO] {message}{Style.RESET_ALL}")
            self.log_file.write(f"[{datetime.datetime.now()}] [INFO] {message}\n")
        elif type == "error":
            print(f"{self.error}[{datetime.datetime.now()}] [ERROR] {message}{Style.RESET_ALL}")
            self.log_file.write(f"[{datetime.datetime.now()}] [ERROR] {message}\n")
        elif type == "success":
            print(f"{self.success}[{datetime.datetime.now()}] [SUCCESS] {message}{Style.RESET_ALL}")
            self.log_file.write(f"[{datetime.datetime.now()}] [SUCCESS] {message}\n")
        elif type == "warning":
            print(f"{self.warning}[{datetime.datetime.now()}] [WARNING] {message}{Style.RESET_ALL}")
            self.log_file.write(f"[{datetime.datetime.now()}] [WARNING] {message}\n")
        else:
            print(f"[{datetime.datetime.now()}] {message}")
            self.log_file.write(f"[{datetime.datetime.now()}] {message}\n")