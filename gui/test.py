import subprocess
# import threading
# import pexpect
# import time

# def run_command_in_terminal(command, duration):
#     # Function to run the command in a terminal
#     def run_command():
#         terminal = pexpect.spawn(command)
#         time.sleep(duration)
#         # Send Ctrl+C
#         terminal.sendintr()
#         terminal.close()
    
#     # Create a thread to run the command
#     command_thread = threading.Thread(target=run_command)
#     command_thread.start()

# if __name__ == "__main__":
#     selected_interface = 'eth0'
#     target_ip = "192.168.2.9"
#     gateway_ip = "192.168.2.254"
    
#     # Flag to determine if the program should quit after running the command
#     should_quit = True
    
#     # Duration to keep the terminal open (in seconds)
#     duration = 5 if should_quit else 0
    
#     # Command to run in the terminal
#     command_1 = f"sudo arpspoof -i {selected_interface} -t {target_ip} {gateway_ip}"
#     command_2 = f"sudo arpspoof -i {selected_interface} -t {gateway_ip} {target_ip}"
    
#     # Run each command in a terminal using threading
#     run_command_in_terminal(command_1, duration)
#     run_command_in_terminal(command_2, duration)
import subprocess


def check_rule_exist(target_ip, action):
    try:
        # Get the output of iptables -S
        output = subprocess.run(["iptables", "-L", "--line-numbers"], capture_output=True, text=True, check=True).stdout
        # Split the output into lines
        lines = output.splitlines()

        # Iterate over each line to check for matching rules
        for line in lines:
            if action in line and target_ip in line:
                print(line)
                return True
        return False
    except subprocess.CalledProcessError as e:
        return False, e.stderr  # Error occurred



def allow_all_connections(target_ip):
    try:
        # Check if DROP rule already exists
        if check_rule_exist(target_ip, "DROP"):
            print(f"[+] DROP rule in table for {target_ip}")
            # Delete the DROP rule
            subprocess.run(["iptables", "-D", "INPUT", "-s", target_ip, "-j", "DROP"])
            subprocess.run(["iptables", "-D", "OUTPUT", "-d", target_ip, "-j", "DROP"])
            print(f"[+] DROP rule DELETED for {target_ip}")
    except Exception as e:
        print(f"[-] An error has occurred while deleting DROP rule for {target_ip}\t{e}")
    
    try:
        # Check if ACCEPT rule already exists
        if not check_rule_exist(target_ip, "ACCEPT"):
            # Add rule to allow all connections from and to the target IP
            subprocess.run(["iptables", "-I", "INPUT", "-s", target_ip, "-j", "ACCEPT"])
            subprocess.run(["iptables", "-I", "OUTPUT", "-d", target_ip, "-j", "ACCEPT"])
            print(f"[+] ACCEPTING ALL TRAFFIC for:   {target_ip}")
    except Exception as e:
        print(f"[-] An error has occurred while ACCEPTING all traffic for {target_ip}\t{e}")
    

def deny_all_connections(target_ip):
    try:
        # Check if ACCEPT rule already exists
        if check_rule_exist(target_ip, "ACCEPT"):
            print(f"[+] ACCEPT rule already in table for {target_ip}")
            # Delete the ACCEPT rule
            subprocess.run(["iptables", "-D", "INPUT", "-s", target_ip, "-j", "ACCEPT"])
            subprocess.run(["iptables", "-D", "OUTPUT", "-d", target_ip, "-j", "ACCEPT"])
            print(f"[+] ACCEPT rule DELETED for {target_ip}")
    except Exception as e:
        print(f"[-] An error has occurred while deleting ACCEPT rule for {target_ip}\t{e}")
    
    
    try:
        # Check if DROP rule already exists
        if not check_rule_exist(target_ip, "DROP"):
            # Add rule to drop all connections from and to the target IP
            subprocess.run(["iptables", "-I", "INPUT", "-s", target_ip, "-j", "DROP"])
            subprocess.run(["iptables", "-I", "OUTPUT", "-d", target_ip, "-j", "DROP"])
            print(f"[+] DROPPING ALL TRAFFIC for:  {target_ip}")
    except Exception as e:
        print(f"[-] An error has occurred while DROPPING all traffic rule for {target_ip}\t{e}")

    

# Example usage
target_ip = "192.168.2.4"
allow_all_connections(target_ip)
# Alternatively, you can use:
# deny_all_connections(target_ip)
# import subprocess

# def print_table():
#     # Print the current rules in the iptables table
#     subprocess.run(["iptables", "-L", "-n", "-v"])

# def read_rules():
#     # Read all the rules in the iptables table
#     output = subprocess.run(["iptables", "-S"], capture_output=True, text=True)
#     return output.stdout

# # Example usage1
# print_table()
# rules = read_rules()
# print(rules)
