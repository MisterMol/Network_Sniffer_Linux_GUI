import subprocess
from scapy import packet
import scapy.all as scapy
from scapy.layers import http
import time
import os
import sys
import signal
import socket
import csv

def check_sudo():
    return 'SUDO_USER' in os.environ

# Function to handle KeyboardInterrupt (Ctrl+C)
def signal_handler(sig, frame):
    print("\nCtrl+C detected. Exiting...")
    exiting()

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)


# Function to handle exiting
def exiting():
    print("Terminating Program ...")
    restart_network_manager()
    print("Discovered Hosts:")
    for host_id, host_info in discovered_hosts.items():
        print(f"Host ID: {host_id:<5} | {host_info['ip_address']:<15} | {host_info['mac_address']:<22} | {host_info['Vendor']:<45} | {host_info['Hostname']}")
    sys.exit()

# Function to restart NetworkManager service
def restart_network_manager():
    print("Restarting NetworkManager service...")
    subprocess.run(['sudo', 'systemctl', 'restart', 'NetworkManager'])

# Function to get all the interfaces
def get_interfaces():
    try:
        output = subprocess.check_output(['ifconfig'], universal_newlines=True)
        lines = output.split('\n')
        interfaces = []

        for line in lines:
            if line.strip() and not line.startswith(' '):
                interface = line.split(':')[0]
                interfaces.append(interface)

        return interfaces

    except Exception as e:
        print(f"Error: {e}")

# Function to let the user select an interface
def select_interface(interfaces):
    global select_interface
    if interfaces:
        print("Selectable interfaces:")
        for i, interface in enumerate(interfaces):
            print(f"{i}. {interface}")
        
        print("x. Enter 'x' to exit")
        selected_interface = input("\nEnter the number of the interface you want to select: ")

        if selected_interface.lower() == 'x':
            exiting()
            return

        try:
            selected_interface = int(selected_interface)
            if selected_interface >= 0 and selected_interface < len(interfaces):
                chosen_interface = str(interfaces[selected_interface])
                print(f"You selected interface: {chosen_interface}\n")
                return str(interfaces[selected_interface])
            else:
                print("Invalid.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    else:
        print("No valid interfaces found.")



def network_sniff(interface):
    scapy.sniff(iface=interface, store=False, prn=sniffed_packet)

def get_hostnames(ip_address):
    def get_hostname_by_dns(ip_address):
        try:
            hostname, _, _ = socket.gethostbyaddr(ip_address)
            return [hostname]
        except socket.herror:
            return []

    def get_hostname_by_reverse_dns(ip_address):
        try:
            _, _, hostnames = socket.gethostbyaddr(ip_address)
            return hostnames
        except socket.herror:
            return []

    # Try DNS lookup
    hostnames = get_hostname_by_dns(ip_address)

    if not hostnames:
        # If DNS lookup didn't return anything, try reverse DNS lookup
        hostnames = get_hostname_by_reverse_dns(ip_address)

    return hostnames

def get_manufacturer_oui(mac_address):
    oui = mac_address[:8]
    return oui

def get_vendor_from_mac(mac_address):
    with open(r'gui/macvendors/mac-vendors-export.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        mac_address = mac_address.upper()
        mac = get_manufacturer_oui(mac_address)
        for row in csv_reader:
            if mac == row['Mac Prefix']:
                return row['Vendor Name']
    return ""

discovered_hosts = {}

def add_host_to_discover_dict(ip_address, mac_address):
    # Check if the MAC address already exists in discovered_hosts
    for host_id, host_info in discovered_hosts.items():
        if host_info["mac_address"] == mac_address:
            print(host_id, "MAC ADDRESS ALREADY IN TABLE!")
            # If the MAC address exists, return without adding the host
            return

    # Check if the IP address already exists in discovered_hosts
    for host_id, host_info in discovered_hosts.items():
        if host_info["ip_address"] == ip_address:
            # If the IP address exists, update the MAC address
            host_info["mac_address"] = mac_address
            return

    # If the IP address doesn't exist, add a new host
    host_id = len(discovered_hosts) + 1
    vendor = get_vendor_from_mac(mac_address)

    hostnames = get_hostnames(ip_address)
    if hostnames:
        hostname = hostnames[0]
    else:
        hostname = ""

    host_info = {
        "mac_address": mac_address,
        "ip_address": ip_address,
        "Vendor": vendor, 
        "Hostname": hostname,  
    }

    discovered_hosts[host_id] = host_info



def check_used_application(string_from_packet, src_mac, dst_mac):
    applications = [
        'industrialandcommercialbankofchinalimited', 'nationale-nederlandenbank', 'garantibankinternational', 'medicibankinternational', 'yapikredibanknederland', 'microsoftauthenticator', 'nationale-nederlanden', 
        'deutschebanknederland', 'nationalenederlanden', 'hofhoornemanbankiers', 'westlandutrechtbank', 'vanlanschotbankiers', 'vanlanschotkempen', 'popcorntimeonline', 'oranjeinvestments', 'hofhoornemanohpen', 'whatsappbusiness', 
        'translate.google', 'merriam-webster', 'easportspornhub', 'dpboss.services', 'constantcontact', 'clevelandclinic', 'christianmingle', 'campaignmonitor', 'tulphypotheken', 'microsoftteams', 'jetpackjoyride', 'demir-halkbank', 
        'candycrushsaga', 'activecampaign', 'subwaysurfers', 'subwayservers', 'seatsandsofas', 'rijksoverheid', 'leaseplanbank', 'handelsbanken', 'frieslandbank', 'eightballpool', 'telefoonboek', 'mobilemonkey', 'espncricinfo', 'elitesingles', 
        'deutschebank', 'clickfunnels', 'clashofclans', 'woocommerce', 'vanlanschot', 'tripadvisor', 'triodosbank', 'squarespace', 'speeleiland', 'popcorntime', 'monutatrust', 'monopoly go', 'medlineplus', 'innercircle', 'hubspotchat', 
        'gotomeeting', 'getresponse', 'crunchyroll', 'clashroyale', 'bigcommerce', 'amazonprime', 'albertheijn', 'accuweather', 'abnamrobank', ' tunnelbear', 'yachtlease', 'windscribe', 'wetransfer', 'videoprime', 'trustpilot', 'streamyard', 
        'sendinblue', 'salesforce', 'royalmatch', 'primevideo', 'prestashop', 'nibcdirect', 'mayoclinic', 'mailerlite', 'mail.yahoo', 'indiatimes', 'healthline', 'googlemeet', 'googlemaps', 'googlehome', 'friendster', 'foursquare', 'expressvpn', 
        'disneyplus', 'cyberghost', 'convertkit', 'candycrush', 'callofduty', 'britannica', 'blackboard', 'wordpress', 'wikipedia', 'tokopedia', 'theleague', 'teamspeak', 'surfshark', 'speedtest', 'sparkpost', 'sofascore', 'regiobank', 
        'protonvpn', 'pinterest', 'pinduoduo', 'peacocktv', 'obsstudio', 'microsoft', 'messenger', 'mailchimp', 'leaseplan', 'leadpages', 'jiocinema', 'instapage', 'instagram', 'helpscout', 'freshdesk', 'decathlon', 'cambridge', 'autopilot', 
        'appear.in', '8ballpool', 'xhamster', 'whatsapp', 'volusion', 'ventrilo', 'unbounce', 'telegram', 'snapchat', 'savefrom', 'rabobank', 'overheid', 'opencart', 'nibcbank', 'monopoly', 'manychat', 'ludoking', 'livechat', 'linkedin', 
        'knabbank', 'intercom', 'ilovepdf', 'hurriyet', 'hangouts', 'groovehq', 'frontapp', 'fortnite', 'flipkart', 'facebook', 'eharmony', 'chatfuel', ' vyprvpn', ' thefork', 'zendesk', 'zalando', 'youtube', 'xvideos', 'webflow', 'weather', 
        'walmart', 'viaplay', 'twitter', 'triodos', 'spotify', 'snsbank', 'shopify', 'samsung', 'rakuten', 'phonepe', 'peacock', 'outlook', 'okcupid', 'nytimes', 'nordvpn', 'netflix', 'myspace', 'moosend', 'moneyou', 'mailjet', 'mailgun', 
        'magento', 'madmimi', 'landbot', 'klaviyo', 'join.me', 'jetpack', 'ingbank', 'hubspot', 'dumpert', 'disney+', 'discord', 'chatgpt', 'booking', 'bngbank', 'blokker', 'blogger', 'bigbank', 'asnbank', 'appletv', 'abnamro', 'yandex', 
        'xsplit', 'weebly', 'wechat', 'vinted', 'twitch', 'tumblr', 'tinder', 'tiktok', 'taobao', 'tagged', 'sunweb', 'spboss', 'signal', 'safari', 'roblox', 'reddit', 'paypal', 'openai', 'nubank', 'mumble', 'meetup', 'meesho', 'medium', 
        'joomla', 'indeed', 'icloud', 'hbomax', 'grindr', 'google', 'fandom', 'drupal', 'douyin', 'disney', 'deezer', 'clover', 'capcut', 'bumble', 'aweber', 'amazon', 'alipay', 'zoosk', 'ziggo', 'yahoo', 'webex', 'vimeo', 'viber', 'tesco', 
        'tenor', 'tele2', 'teams', 'steam', 'spele', 'slack', 'skype', 'simyo', 'shein', 'quora', 'prime', 'orkut', 'odido', 'match', 'jumbo', 'jitsi', 'jdate', 'icbcs', 'hinge', 'happn', 'hanze', 'gmail', 'globo', 'giphy', 'gamma', 'funda', 
        'drift', 'crisp', 'canva', 'badoo', 'apple', 'adobe', 'zoom', 'zoho', 'yelp', 'xnxx', 'waze', 'uber', 'toto', 'temu', 'tawk', 'rabo', 'nike', 'nibc', 'line', 'knab', 'imdb', 'ikea', 'hulu', 'etsy', 'espn', 'emma', 'ebay', 'drip', 'bebo', 
        'wix', 'uol', 'sns', 'pof', 'kpn', 'kik', 'hi5', 'hbo', 'bng', 'bbc', 'asn'
        ]

    websites = [
        'maastrichtuniversity.nl', 'nationalgeographic.com', 'hogeschoolrotterdam.nl', 'vanlanschotkempen.com', 'universiteitleiden.nl', 'tilburguniversity.edu', 'theweathernetwork.com', 'popcorntimeonline.xyz', 
        'outlook.office365.com', 'gemeente.groningen.nl', 'vanlanschotkempen.nl', 'oranjeinvestments.nl', 'mail.google.com/chat', 'www.google.com/maps', 'teams.microsoft.com', 'hangouts.google.com', 'christianmingle.com', 
        'calendar.google.com', 'businessinsider.com', 'weatherchannel.com', 'washingtonpost.com', 'chicagotribune.com', 'bleacherreport.com', 'tulphypotheken.nl', 'thedailybeast.com', 'stackoverflow.com', 'stackexchange.com', 
        'outlook.office365', 'independent.co.uk', 'demir-halkbank.nl', 'yapikredibank.nl', 'yahooweather.com', 'wunderground.com', 'web.telegram.org', 'rijksoverheid.nl', 'outlook.live.com', 'mijn.overheid.nl', 'metoffice.gov.uk', 
        'leaseplanbank.nl', 'handelsbanken.nl', 'frieslandbank.nl', 'elitesingles.com', 'businessweek.com', 'bbcweather.co.uk', 'ars technica.com', 'vvvnederland.nl', 'venturebeat.com', 'play.google.com', 'outlook.live.nl', 'news.google.com', 
        'mijnoverheid.nl', 'meet.google.com', 'innercircle.com', 'hofhoorneman.nl', 'google.com/chat', 'deutschebank.nl', 'crunchyroll.com', 'cntraveller.com', 'calendar.google', 'accuweather.com', 'vanlanschot.nl', 'techcrunch.com', 
        'starchannel.nl', 'primevideo.com', 'monutatrust.nl', 'marktplaats.nl', 'login.live.com', 'lifehacker.com', 'google.nl/maps', 'garantibank.nl', 'duckduckgo.com', 'disneyplus.com', 'consent.google', 'aolweather.com', 'aliexpress.com', 
        'yachtlease.nl', 'wordpress.org', 'wikipedia.org', 'weeronline.nl', 'volkskrant.nl', 'topbloemen.nl', 'theleague.com', 'pinterest.com', 'peacocktv.com', 'parrotsec.org', 'nibcdirect.nl', 'newyorker.com', 'microsoft.com', 'messenger.com', 
        'medicibank.nl', 'mediamarkt.nl', 'instagram.com', 'crazyshit.com', 'buienradar.nl', 'buienalarm.nl', 'bloomberg.com', 'aljazeera.com', 'whatsapp.com', 'usatoday.com', 'tv.apple.com', 'telegraaf.nl', 'snapchat.com', 'regiobank.nl', 
        'outlook.live', 'mashable.com', 'linkedin.com', 'huffpost.com', 'guardian.com', 'facebook.com', 'engadget.com', 'eharmony.com', 'drive.google', 'decathlon.nl', 'buzzfeed.com', 'youtube.com', 'weather.com', 'vodafone.nl', 'twitter.com', 
        'spotify.com', 'reuters.com', 'rabobank.nl', 'play.google', 'overheid.nl', 'okcupid.com', 'nytimes.com', 'news.google', 'netflix.com', 'nbcnews.com', 'meet.google', 'latimes.com', 'hsleiden.nl', 'gizmodo.com', 'foxnews.com', 
        'discord.com', 'coolblue.nl', 'chatgpt.com', 'cbsnews.com', 'blogger.com', 'bestbuy.com', 'bbcnews.com', 'abcnews.com', 'ziggogo.tv', 'zalando.nl', 'yandex.com', 'wehkamp.nl', 'wechat.com', 'vandale.nl', 'utwente.nl', 'tumblr.com', 
        'tudelft.nl', 'triodos.nl', 'tmobile.nl', 'tinder.com', 'tiktok.com', 'target.com', 'snsbank.nl', 'reddit.com', 'paypal.com', 'openai.com', 'office.com', 'moneyou.nl', 'medium.com', 'login.live', 'hbomax.com', 'grindr.com', 'google.com', 
        'github.com', 'forbes.com', 'flickr.com', 'clover.com', 'bumble.com', 'boston.com', 'bngbank.nl', 'blokker.nl', 'bigbank.nl', 'asnbank.nl', 'amazon.com', 'action.com', 'abnamro.nl', 'zoosk.com', 'yahoo.com', 'wired.com', 'vinted.nl', 
        'viber.com', 'twitch.tv', 'tvgids.nl', 'tenor.com', 'slate.com', 'slack.com', 'skype.com', 'quora.com', 'postnl.nl', 'match.com', 'jumbo.com', 'jdate.com', 'indeed.nl', 'imgur.com', 'hinge.com', 'happn.com', 'greetz.nl', 'google.nl', 
        'giphy.com', 'fundap.nl', 'fontys.nl', 'conrad.nl', 'baidu.com', 'badoo.com', 'apple.com', 'amazon.nl', 'amazon.de', 'albert.nl', 'trouw.nl', 'time.com', 'temu.com', 'phys.org', 'pathé.nl', 'ohpen.nl', 'noaa.gov', 'nmap.org', 'ncaa.com', 
        'kali.org', 'icbcs.nl', 'hulu.com', 'hanze.nl', 'gamma.nl', 'etsy.com', 'espn.com', 'ebay.com', 'digid.nl', 'cnet.com', 'cnbc.com', 'bing.com', 'avans.nl', 'zoom.us', 'wsj.com', 'vox.com', 'rtlz.nl', 'pof.com', 'npr.org', 'nibc.nl', 
        'nhl.com', 'nfl.com', 'nba.com', 'mlb.com', 'line.me', 'kpn.com', 'knab.nl', 'kik.com', 'hema.nl', 'ebay.nl', 'cnn.com', 'bol.com', 'bbc.com', 'ans.app', 'wur.nl', 'uva.nl', 'rug.nl', 'rtl.nl', 'nrc.nl', 'npo.nl', 'nos.nl', 'ing.nl', 
        'hva.nl', 'han.nl', 'eur.nl', 'x.com', 'vu.nl', 'uu.nl', 'ru.nl', 'ou.nl', 'nu.nl', 'hu.nl', 'fd.nl', 'de.nl', 'ah.nl', 'ad.nl'
        ]

    not_useful_data = ["googlecast", "googleapis", "googlezone", "pki-g", 'mijnmodem.kpn.home']

    # controleer voor niet nuttige data
    skip_processing = False
    for not_useful in not_useful_data:
        if not_useful in string_from_packet:
            skip_processing = True
            break

    # overslaan van verwerking als niet nuttige data wordt gevonden
    if not skip_processing:
        website_hit = False
        for website in websites:
            if website in string_from_packet:
                print(f"Visiting website: www.{website:<20} | MAC SRC: {src_mac:<30} | MAC DST: {dst_mac:<40}")
                website_hit = True
                break

        if not website_hit:
            for app in applications:
                if app in string_from_packet:
                    print(f"Visiting application: {app.capitalize():<20} | MAC SRC: {src_mac:<30} | MAC DST: {dst_mac:<40}")
                    break
        
    
    print(string_from_packet)



# Example usage in sniffed_packet function
def sniffed_packet(packet):
    with open('output.txt', 'a') as f:
        if packet:
            if packet.haslayer("Ethernet"):
                sniffed_packet_ethernet_src = packet["Ethernet"].src
                print("Packet MAC SRC ==  ", sniffed_packet_ethernet_src)
                sniffed_packet_ethernet_dst = packet["Ethernet"].dst
                print("Packet MAC DST ==  ", sniffed_packet_ethernet_dst)
            else:
                sniffed_packet_ethernet_src = 'No ETHERNET src Found!'
                sniffed_packet_ethernet_dst = 'No ETHERNET dst Found!'
            if packet.haslayer("IP"):
                sniffed_packet_ip_src = packet["IP"].src
                print("Packet IP SRC ==  ", sniffed_packet_ip_src)
                sniffed_packet_ip_dst = packet["IP"].dst
                print("Packet IP DST ==  ", sniffed_packet_ip_dst)
            else:
                sniffed_packet_ip_src = 'No IP src Found!'
                sniffed_packet_ip_dst = 'No IP dst Found!'
            if packet.haslayer("DNS"):
                dns = packet.getlayer("DNS")
                if dns.qd:
                    qname = dns.qd.qname.decode('utf-8')
                    print("DNS QNAME == ", qname, file=f)
                    check_used_application(qname, sniffed_packet_ethernet_src, sniffed_packet_ethernet_dst)
                if dns.an:
                    for ans in dns.an:
                        rrname = ans.rrname.decode('utf-8')
                        if rrname:
                            check_used_application(rrname, sniffed_packet_ethernet_src, sniffed_packet_ethernet_dst)
                            print("DNS RRNAME == ", rrname, file=f)
                        if hasattr(ans, "rdata"): 
                            rdata = ans.rdata
                            if isinstance(rdata, bytes):  # Check if rdata is bytes
                                rdata = rdata.decode('utf-8') 

                            check_used_application(rdata, sniffed_packet_ethernet_src, sniffed_packet_ethernet_dst)
                            print("DNS RDATA == ", rdata, file=f)
                    try:
                        add_host_to_discover_dict(sniffed_packet_ip_dst, sniffed_packet_ethernet_dst)
                        add_host_to_discover_dict(sniffed_packet_ip_src, sniffed_packet_ethernet_src)
                    except Exception as e:
                        print("An error has occurred while adding a host to the dictionary!: ", e, file=f)


if __name__ == "__main__":
    if not check_sudo():
        print("This program is not run with sudo privileges.")
        print("Try running it with sudo", file=sys.stderr)
        sys.exit()
    else:
        pass


    interfaces = get_interfaces()
    selected_interface = select_interface(interfaces)


    # set_interface_in_monitor_mode(select_interface)
    print(selected_interface)

    # Dict van Ontdekte hosts:

    # Functie die snifft (sniffer)
    network_sniff(selected_interface)

    # Functie die bekijkt of de hosts al in de discoverd_hosts dictionary zit, zo niet voegt de functe deze toe met een ID.

    # Functie die de output van de sniffer analyseert en IP-Adressen, Mac,adressen, Hostname achterhaalt en opslaat in een tabel.

    # Functie die het netwerkverkeer van de sniffer analyseert en kijkt welke applicaties actief zijn (Spotify, Netflix, Google, Deezer, Googleanalytics, Youtube, Chromecast, Disney+, Viaplay, ,Bezochte Websites)
    # En deze koppelt aan het apparaat die ze bezoekt (MAC/IP/Hostname)

    print("Discovered Hosts:")
    for host_id, host_info in discovered_hosts.items():
        print(f"Host ID: {host_id:<5} | {host_info['ip_address']:<15} | {host_info['mac_address']:<22} | {host_info['Vendor']:<28} | {host_info['Hostname']:<35}")
