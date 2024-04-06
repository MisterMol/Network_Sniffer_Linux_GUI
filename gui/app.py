import traceback
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import subprocess
import time
from scapy.all import *
import scapy.all as scapy
import time
import os
import tldextract
import socket
import csv
import threading
from flask import jsonify

app = Flask(__name__)

app.secret_key = 'Secret_Sniffer_Key_Ayo' 

sniffer_running = False
sniffer_thread = None
selected_interface = None

# Threads voor het kijken welke programma's actief zijn en deze te weergeven op index.html
active_threads = set()  


@app.route('/', methods=['GET'])
def selecting_available_interface() -> str:
    try:
        output = subprocess.check_output(['ifconfig'], universal_newlines=True)
        lines = output.split('\n')
        interfaces = []

        for line in lines:
            if line.strip() and not line.startswith(' '):
                interface = line.split(':')[0]
                interfaces.append(interface)
        return render_template('choose_network_adapter.html', interfaces=interfaces)

    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred"


@app.route('/dashboard', methods=['GET', 'POST'])
def index():
    global selected_interface
    if request.method == 'POST':
        selected_interface = request.form.get('interface')
        return render_template("index.html", interface=selected_interface, sniffer_running=sniffer_running, discovered_hosts=discovered_hosts)
    else:
        # Handle the case where the user directly accesses the /dashboard route
        return redirect(url_for('selecting_available_interface'))

def network_sniff(interface):
    global sniffer_running
    
    while sniffer_running:
        try:
            scapy.sniff(iface=interface, store=False, prn=sniffed_packet)
        except Exception as e:
            print("An error occurred while sniffing packets:", e)
            traceback.print_exc()

    print("Sniffer stopped")


@app.route('/start_stop_sniffer', methods=['POST'])
def start_stop_sniffer():
    global sniffer_running, sniffer_thread, selected_interface

    # Toggle the sniffer status
    sniffer_running = not sniffer_running
    print(sniffer_running)
    
    if sniffer_running:
        # Start the sniffer thread if not already running
        if not sniffer_thread or not sniffer_thread.is_alive():
            if selected_interface:
                sniffer_thread = threading.Thread(target=network_sniff, args=(selected_interface,))
                sniffer_thread.start()
                print("Sniffer started on interface:", selected_interface)
            else:
                print("No interface selected. Cannot start sniffer.")
        else:
            print("Sniffer thread is already running.")
    else:
        # Stop the sniffer
        if sniffer_thread and sniffer_thread.is_alive():
            sniffer_running = False  # Stop the sniffer loop
            sniffer_thread.join()    # Wait for the thread to finish
            print("Sniffer stopped")
        else:
            print("Sniffer thread is not running.")

    return jsonify({'sniffer_running': sniffer_running})



def get_hostnames(ip_address):
    def get_hostname_by_dns(ip_address):
        try:
            hostname, _, _ = socket.gethostbyaddr(ip_address)
            return [hostname]
        except socket.herror:
            return []
        except socket.gaierror as e:
            print(f"Error resolving hostname for {ip_address}: {e}")
            hostname = None  # or any fallback value

    def get_hostname_by_reverse_dns(ip_address):
        try:
            _, _, hostnames = socket.gethostbyaddr(ip_address)
            return hostnames
        except socket.herror:
            return []
        except socket.gaierror as e:
            print(f"Error resolving hostname for {ip_address}: {e}")
            hostname = None  # or any fallback value

    # Try DNS lookup
    hostnames = get_hostname_by_dns(ip_address)

    if not hostnames:
        # If DNS lookup didn't return anything, try reverse DNS lookup
        hostnames = get_hostname_by_reverse_dns(ip_address)

    return hostnames


def get_vendor_from_mac(mac_address):
    with open(r'gui/macvendors/mac-vendors-export.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        mac_address = mac_address.upper()
        mac = mac_address[:8]
        for row in csv_reader:
            if mac == row['Mac Prefix']:
                return row['Vendor Name']
    return ""

def extract_domain(url):
    extracted = tldextract.extract(url)
    domain = extracted.domain if extracted.domain else None
    return domain

import os

def find_matching_icons(input_website):
    icons_folder = "gui/static/icon_folder/"
    icons = os.listdir(icons_folder)
    
    matching_icons = []
    icons_folder = "static/icon_folder/"
    domain = extract_domain(input_website)
    if domain:
        input_website = domain
    
    # First, look for an exact match
    for icon in icons:
        # Remove the file extension
        icon_name = os.path.splitext(icon)[0]
        
        # Check if the website name exactly matches the icon name
        if input_website == icon_name:
            matching_icons.append(os.path.join(icons_folder, icon))
            return matching_icons
    
    # If no exact match is found, look for partial matches
    for icon in icons:
        # Remove the file extension
        icon_name = os.path.splitext(icon)[0]
        
        # Check if the website name is contained in the icon name
        if input_website in icon_name:
            matching_icons.append(os.path.join(icons_folder, icon))
    
    if not matching_icons:
        matching_icons.append(os.path.join(icons_folder, "gray_picture_if_none_found.jpeg"))
    
    return matching_icons



discovered_hosts = {}

skip_display_mac_address = []

active_dict = {}
inactive_dict = {}

@app.route("/activate_host", methods=["POST"])
def activate_host():
    data = request.get_json()
    mac_address = data.get("mac_address")
    do_not_display = data.get("do_not_display")
    
    if mac_address is not None:
        if do_not_display: 
            if mac_address not in skip_display_mac_address:
                skip_display_mac_address.append(mac_address)
        else:
            if mac_address in skip_display_mac_address:
                skip_display_mac_address.remove(mac_address)  

        return jsonify({"message": "Host status updated successfully"}), 200
    else:
        return jsonify({"error": "MAC address not provided"}), 400

@app.route("/send_hosts_dict")
def sending_host_dictionary_to_javascript():
    updated_discovered_hosts = {}
    for host_id, host_info in discovered_hosts.items():
        mac_address = host_info["mac_address"]
        if mac_address in skip_display_mac_address:
            host_info["do_not_display"] = True
        elif mac_address not in skip_display_mac_address:
            host_info["do_not_display"] = False
        updated_discovered_hosts[host_id] = host_info
    return jsonify(updated_discovered_hosts)


@app.route('/send_host_information_dict')
def sending_host_information_dictionary_to_javascript():
    dict_to_send = {}
    sorted_host_information = sorted(active_dict.items(), key=lambda x: datetime.strptime(x[1]['timestamp'], "%Y-%m-%d %H:%M:%S"), reverse=True)
    for (mac_address, website), value in sorted_host_information:
        if mac_address not in skip_display_mac_address:
            matching_icons = find_matching_icons(website)
            icon_url = matching_icons[0] if matching_icons else None 
            website_visits = value['website_times_visited']
            key = {'mac_address': mac_address, 'website_or_app': website, 'times_visited': website_visits, 'icon_url': icon_url, 'timestamp': value['timestamp']}
            dict_to_send[str((mac_address, website))] = key
        print(sorted_host_information)
    return jsonify({'host_information': dict_to_send, 'skip_display_mac_address': skip_display_mac_address})



def add_host_to_discover_dict(ip_address, mac_address):
    # Check if the IP address / MAC address already exists in discovered_hosts
    for host_id, host_info in discovered_hosts.items():
        if host_info["ip_address"] == ip_address:
            return
        elif host_info["mac_address"] == mac_address:
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
        "vendor": vendor, 
        "hostname": hostname,
        "do_not_display": False,
    }
    discovered_hosts[host_id] = host_info


class TimerThread(threading.Thread):
    def __init__(self, website, mac_address, active_dict, inactive_dict):
        super().__init__()
        # Initialize the thread with website, MAC address, and dictionaries
        self.website = website
        self.mac_address = mac_address
        self.active_dict = active_dict
        self.inactive_dict = inactive_dict
        # Lock to ensure thread safety
        self.lock = threading.Lock()
        # Timer settings
        self.timer = 25  # Initial timer value
        self.running = False  # Flag to control thread execution

    def run(self):
        self.running = True
        while self.timer > 0:
            with self.lock:
                if not self.running:
                    break
                # Display remaining time
                # print(f"Timer for '{self.website}' searched by MAC {self.mac_address} : {self.timer}")
                self.timer -= 1
            time.sleep(1)  # Wait for 1 second

        # Timer has run out, move data if it exists
        with self.lock:
            if (self.mac_address, self.website) in self.active_dict:
                # Move data from active to inactive dictionary
                inactive_key = (self.mac_address, self.website)
                active_key = (self.mac_address, self.website)
                inactive_data = self.active_dict.pop(active_key)
                if inactive_key in self.inactive_dict:
                    # If already in inactive_dict, increment the count
                    inactive_data['website_times_visited'] += 1

                self.inactive_dict[inactive_key] = inactive_data
                # Remove thread from active_threads
                active_threads.remove((self.mac_address, self.website))
                # Print status
                print(f"Search for '{self.website}' by MAC {self.mac_address} completed and moved to inactive_dict.")
                print(f"Search count for '{self.website}' by MAC {self.mac_address}: {inactive_data['website_times_visited']}")
                print(f"Timer has ended for: MAC Address - {self.mac_address}, Website - {self.website}")

    def reset_timer(self):
        # Reset timer to its initial value
        with self.lock:
            self.timer = 25

    def stop_timer(self):
        # Stop the timer thread
        with self.lock:
            self.running = False

from datetime import datetime

def add_host_to_active_dict(mac_address_source, website_or_app):
    global active_dict
    global inactive_dict
    global active_threads
    
    # Vang de huidige tijd op
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if there's already an active timer thread for this MAC address and website
    if (mac_address_source, website_or_app) in active_threads:
        # If so, find the thread and reset its timer
        for thread in threading.enumerate():
            if isinstance(thread, TimerThread) and thread.website == website_or_app and thread.mac_address == mac_address_source:
                # print(f"\n\n\nResetting timer for website '{website_or_app}' searched by MAC {mac_address_source}\n\n")
                thread.reset_timer()
                break

    else:
        # If not, create a new timer thread
        timer_thread = TimerThread(website_or_app, mac_address_source, active_dict, inactive_dict)
        timer_thread.start()
        active_threads.add((mac_address_source, website_or_app))
        # Add the thread to active threads set

        # Add the MAC address, website, and timestamp to active_dict
        active_key = (mac_address_source, website_or_app)
        if active_key in inactive_dict:
            # If the host is in the inactive_dict, increase 'website_times_visited' by 1
            inactive_dict[active_key]['website_times_visited'] += 1
            # Move the host from inactive_dict to active_dict and add timestamp
            inactive_dict[active_key]['timestamp'] = current_time
            active_dict[active_key] = inactive_dict.pop(active_key)
        else:
            # If the host is not in inactive_dict, set 'website_times_visited' to 1 and add timestamp
            active_dict[active_key] = {'website_times_visited': 1, 'timestamp': current_time}



def check_used_application(string_from_packet, src_mac, dst_mac, discovered_hosts):
    
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
        'tenor', 'tele2', 'teams', 'steam', 'spele', 'slack', 'skype', 'simyo', 'shein', 'quora', 'prime', 'orkut', 'odido', 'jumbo', 'jitsi', 'jdate', 'icbcs', 'hinge', 'happn', 'hanze', 'gmail', 'globo', 'giphy', 'gamma', 'funda', 
        'drift', 'crisp', 'canva', 'badoo', 'apple', 'adobe', 'zoho', 'yelp', 'xnxx', 'waze', 'uber', 'toto', 'temu', 'tawk', 'rabo', 'nike', 'nibc', 'line', 'knab', 'imdb', 'ikea', 'hulu', 'etsy', 'espn', 'emma', 'ebay', 'drip', 'bebo', 
        'wix', 'uol', 'sns', 'pof', 'kpn', 'kik', 'hi5', 'hbo', 'bng', 'bbc', 'asn', 'xbox360', 'xbox', 'xboxone', 'playstation', 'playstation4', 'playstation5', 'supercell', 'clashroyale', 'clashofclans', 'marktplaats', 'halfbrick', 'jetpackjoyride',
        'jetpack', 'joyride', 'brawlstars', 'hayday', 'hay-day', 'hay.day', 'brawl.stars', 'udemy', 'loyalty-app.jumbo.com', 'loyalty-app.jumbo.com', 'albertheijn'
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
        'hva.nl', 'han.nl', 'eur.nl', 'x.com', 'vu.nl', 'uu.nl', 'ru.nl', 'ou.nl', 'nu.nl', 'hu.nl', 'fd.nl', 'de.nl', 'ah.nl', 'ad.nl', 'gymshark.com', 'aybl.com', 'offsec.com', 'torproject.org', 'facebook.nl', ' survio.com', 'xbox.com', 'playstation.com',
        'nintendo.nl', 'nintendo.com', 'kaspersky.nl', 'kaspersky.com', 'avg.com', 'encyclo.nl', 'pringles.com', 'lays.nl', 'lays.com', 'mms.com', 'doritos.com', 'doritos.nl', 'dell.com', 'dell.nl', 'intel.com', 'bitcoin.org',
        'marketaxess.com', 'degiro.nl', 'prorealtime.com', 'nerdwallet.com', 'redbull.com', 'redbull.nl', 'milieucentraal.nl', 'ongediertebestrijden.nl', 'groningen.nl', 'fcgroningen.nl', '9292.nl', 'ns.nl', 'arriva.nl', 'qbuzz.nl', 'groningermuseum.nl',
        'epicgames.com', 'mcdonalds.com', 'mcdonalds.nl', 'rituals.com', 'mango.com', 'stoneisland.com', 'supercell.com', 'obsproject.com', 'steampowered.com', 'denon.com', 'jbl.nl', 'ip-tracker.org', 'schiphol.nl', 'klm.nl', 'tui.nl',
        'qatarairways.com', 'singaporeair.com', 'emirates.com', 'ana.co.jp', 'turkishairlines.com', 'swiss.com', 'etihad.com', 'britishairways.com', 'airfrance.com', 'lufthansa.com', 'pathe-thuis.nl', 'nlziet.nl', 'videoland.com', 'npo.nl',
        'udemy.com'
        ]

    not_useful_data = ["googlecast", "googleapis", "googlezone", "pki-g", 'mijnmodem.kpn.home']
    if not isinstance(string_from_packet, str):
        string_from_packet = str(string_from_packet)
    # Controleer voor niet nuttige data
    skip_processing = False
    try:
        for not_useful in not_useful_data:
            # if isinstance(string_from_packet, bytes):
            #     string_from_packet = string_from_packet.decode('utf-8') 
            if not_useful in string_from_packet.lower():
                skip_processing = True
                break

        if not skip_processing and isinstance(string_from_packet, str):  
            website_hit = False
            for website in websites:
                if website in string_from_packet.lower():
                    visited_website = f"www.{website}"
                    print(f"Visiting website: www.{visited_website:<20} | MAC SRC: {src_mac:<30} | MAC DST: {dst_mac:<40}")
                    visited_website = visited_website.lower()
                    add_host_to_active_dict(src_mac, visited_website)
                    website_hit = True
                    break

            if not website_hit:
                for app in applications:
                    if app in string_from_packet.lower():
                        app = app.capitalize()
                        print(f"Visiting application: {app:<20} | MAC SRC: {src_mac:<30} | MAC DST: {dst_mac:<40}")
                        app = app.lower()
                        add_host_to_active_dict(src_mac, app)
                        break

    except Exception as e:
        print(f"An error has occured while trying to guess the used application or website:  {e}")
        traceback.print_exc()

        
from scapy.layers.l2 import Ether

def intercept_packets(packet):
    if packet.haslayer(Ether):  # Controleren op Ethernet-laag
        src_mac = packet[Ether].src  # Bron MAC-adres
        dst_mac = packet[Ether].dst  # Bestemmings-MAC-adres
    else:
        src_mac = dst_mac = None

    if packet.haslayer(IP):
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        protocol = packet[IP].proto
    else:
        # Pakket heeft geen IP-laag, dus we slaan het over
        return

    # Controleren of het protocol TCP of UDP is
    if protocol == 6 and packet.haslayer(TCP):
        src_port = packet[TCP].sport
        dst_port = packet[TCP].dport
    elif protocol == 17 and packet.haslayer(UDP):
        src_port = packet[UDP].sport
        dst_port = packet[UDP].dport
    else:
        src_port = dst_port = None


    populaire_apps = ['industrialandcommercialbankofchinalimited', 'nationale-nederlandenbank', 'garantibankinternational', 'medicibankinternational', 'yapikredibanknederland', 'microsoftauthenticator', 'nationale-nederlanden', 
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
        'tenor', 'tele2', 'teams', 'steam', 'spele', 'slack', 'skype', 'simyo', 'shein', 'quora', 'prime', 'orkut', 'odido', 'jitsi', 'jdate', 'icbcs', 'hinge', 'happn', 'hanze', 'gmail', 'globo', 'giphy', 'gamma', 'funda', 
        'drift', 'crisp', 'canva', 'badoo', 'adobe', 'zoho', 'yelp', 'waze', 'uber', 'temu', 'tawk', 'rabo', 'nike', 'nibc', 'knab', 'imdb', 'ikea', 'hulu', 'etsy', 'espn', 'emma', 'ebay', 'drip', 'bebo', 
        'wix', 'uol', 'sns', 'pof', 'kpn', 'kik', 'bng', 'bbc', 'asn', 'xbox', 'xbox360', 'xboxone', 'playstation', 'playstation4', 'playstation5', 'supercell', 'clashroyale', 'clashofclans', 'marktplaats', 'halfbrick', 'jetpackjoyride',
        'jetpack', 'joyride', 'brawlstars', 'hayday', 'hay-day', 'hay.day', 'brawl.stars', 'udemy', 'loyalty-app.jumbo.com', 'loyalty-app.jumbo.com', 'albertheijn', 'airbnb', "9292", 'oneteam', 'philips',
        'android', 'linux', 'adidas', 'hanzehogeschool', 'mijnoverheid', 'hollandcasino', 'buienalarm', 'steamapps', 'steamapp', 'denon', 'steampowered', 'jumbo']
    if packet.haslayer(Raw):
        payload = packet[Raw].load.decode('utf-8', errors='ignore').lower()  # Omzetten naar kleine letters
        for app in populaire_apps:
            if len(app) >= 3:
                if app.lower() in payload:  # Vergelijken in kleine letters
                    print(f"{app} gevonden in payload:")
                    if src_mac:
                        src_mac = src_mac
                    else:
                        src_mac = "NOTFOUND"
                    
                    if dst_mac:
                        dst_mac = dst_mac
                    else:
                        dst_mac = "NOTFOUND"

                    print(src_mac, dst_mac)
                    # check_used_application(packet, src_mac, dst_mac, discovered_hosts)
                    # print("\n", payload, "\n")
                    print("-" * 50)

def sniffed_packet(packet):
    if packet:
        if packet.haslayer("Ethernet"):
            sniffed_packet_ethernet_src = packet["Ethernet"].src
            # print("Packet MAC SRC ==  ", sniffed_packet_ethernet_src)
            sniffed_packet_ethernet_dst = packet["Ethernet"].dst
            # print("Packet MAC DST ==  ", sniffed_packet_ethernet_dst)
        else:
            sniffed_packet_ethernet_src = 'No ETHERNET src Found!'
            sniffed_packet_ethernet_dst = 'No ETHERNET dst Found!'
        if packet.haslayer("IP"):
            sniffed_packet_ip_src = packet["IP"].src
            # print("Packet IP SRC ==  ", sniffed_packet_ip_src)
            sniffed_packet_ip_dst = packet["IP"].dst
        else:
            sniffed_packet_ip_src = 'No IP src Found!'
            sniffed_packet_ip_dst = 'No IP dst Found!'
        if packet.haslayer("DNS"):
                dns = packet.getlayer("DNS")
                if dns.qd:
                    qname = dns.qd.qname
                    if isinstance(qname, bytes):
                        qname = qname.decode('utf-8', errors='ignore')
                    check_used_application(qname, sniffed_packet_ethernet_src, sniffed_packet_ethernet_dst, discovered_hosts)
                    # print(qname)
                if dns.an:
                    for ans in dns.an:
                        rrname = ans.rrname
                        if isinstance(rrname, bytes):
                            rrname = rrname.decode('utf-8', errors='ignore')
                        if rrname:
                            check_used_application(rrname, sniffed_packet_ethernet_src, sniffed_packet_ethernet_dst, discovered_hosts)
                            # print(rrname)
                        if hasattr(ans, "rdata"):
                            rdata = ans.rdata
                            if isinstance(rdata, bytes):
                                try:
                                    rdata = rdata.decode('utf-8')
                                except UnicodeDecodeError:
                                    pass
                            check_used_application(rdata, sniffed_packet_ethernet_src, sniffed_packet_ethernet_dst, discovered_hosts)
                            # print(rdata)
                try:
                    add_host_to_discover_dict(sniffed_packet_ip_dst, sniffed_packet_ethernet_dst)
                    add_host_to_discover_dict(sniffed_packet_ip_src, sniffed_packet_ethernet_src)
                    return
                except Exception as e:
                    print("An error has occured while adding an host to the dictionary!: ", e)
                    traceback.print_exc()
                    print(f"SRC: {sniffed_packet_ip_src, sniffed_packet_ethernet_src}  DST: {sniffed_packet_ip_dst, sniffed_packet_ethernet_dst}")


if __name__ == "__main__":
    app.run(debug=True)
