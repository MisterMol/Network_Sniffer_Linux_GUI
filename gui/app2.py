from flask import Flask, jsonify, render_template, request, redirect, url_for, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import scapy.all as scapy
import threading
import time
import traceback
import sys
import csv
import socket
import tldextract
from arp_spoof_MITM import run_arpspoof, stop_sniffing
import os
import datetime
import ipaddress
import re
import subprocess


###################################################################################################
##### CONFIG ######################################################################################
###################################################################################################

website_or_applications = ['voetbalwedstrijdenvandaag.nl', 'iknowwhatyoudownload.com', 'teletekst.startpagina.nl', 'torrentz2.nznbcnews.com', 'maastrichtuniversity.nl', 'ongediertebestrijden.nl', 'nationalgeographic.com', 
                           'interactivebrokers.com', 'hogeschoolrotterdam.nl', 'vanlanschotkempen.com', 'tilburguniversity.edu', 'popcorntimeonline.xyz', 'outlook.office365.com', 'gemeente.groningen.nl', 'theweathernetwork.com', 
                           'universiteitleiden.nl', 'oranjeinvestments.nl', 'vanlanschotkempen.nl', 'mail.google.com/chat', 'www.google.com/maps', 'hangouts.google.com', 'calendar.google.com', 'teams.microsoft.com', 'turkishairlines.com', 
                           'christianmingle.com', 'businessinsider.com', 'bleacherreport.com', 'new-123movies.live', 'britishairways.com', 'cryptobriefing.com', 'weatherchannel.com', 'groningermuseum.nl', 'washingtonpost.com', 
                           'kickasstorrents.pw', 'chicagotribune.com', 'cointelegraph.com', 'coinmarketcal.com', 'tulphypotheken.nl', 'demir-halkbank.nl', 'coinmarketcap.com', 'thedailybeast.com', 'outlook.office365', 'milieucentraal.nl', 
                           'independent.co.uk', 'cryptocompare.com', 'stackexchange.com', 'mooistedorpjes.nl', 'stackoverflow.com', 'singaporeair.com', 'metoffice.gov.uk', 'drive.google.com', 'vandaaginside.nl', 'businessweek.com', 
                           'cryptopotato.com', 'bbcweather.co.uk', 'yapikredibank.nl', 'investopedia.com', 'bravenewcoin.com', 'limetorrents.lol', 'seekingalpha.com', 'thepiratebay.org', 'wunderground.com', 'tdameritrade.com', 'handelsbanken.nl', 
                           'leaseplanbank.nl', 'steampowered.com', 'radioveronica.nl', 'qatarairways.com', 'livesoccertv.com', 'forexfactory.com', 'mijn.overheid.nl', 'yahooweather.com', 'tradestation.com', 'frieslandbank.nl', 'web.telegram.org', 
                           '123movies.online', 'outlook.live.com', 'elitesingles.com', 'rijksoverheid.nl', 'magnet-yify.com0', 'marketwatch.com', 'venturebeat.com', 'theguardian.com', 'play.google.com', 'arstechnica.com', 'thuisbezorgd.nl', 
                           'vpnoverview.com', 'hofhoorneman.nl', 'tradingview.com', 'news.google.com', 'calendar.google', 'vvvnederland.nl', 'thinkorswim.com', 'pullandbear.com', 'playstation.com', 'crunchyroll.com', 'prorealtime.com', 
                           'deutschebank.nl', 'cntraveller.com', 'innercircle.com', 'google.com/chat', 'marketaxess.com', 'accuweather.com', 'stockcharts.com', 'meet.google.com', 'stoneisland.com', 'outlook.live.nl', 'chat.openai.com', 
                           'mijnoverheid.nl', 'motleyfool.com', 'marktplaats.nl', 'aolweather.com', 'duckduckgo.com', 'vanlanschot.nl', 'login.live.com', 'consent.google', 'shop.mango.com', 'fcgroningen.nl', 'stadslyceum.nl', 'blockchain.com', 'monutatrust.nl', 
                           'bittorrent.com', 'primevideo.com', 'garantibank.nl', 'nerdwallet.com', 'pathe-thuis.nl', 'starchannel.nl', 'stocktwits.com', 'lifehacker.com', 'disneyplus.com', 'cryptonews.com', 'torproject.org', 'aliexpress.com', 
                           'ip-tracker.org', 'beincrypto.com', 'obsproject.com', 'google.nl/maps', 'techcrunch.com', 'theleague.com', 'robinhood.com', 'newyorker.com', 'instagram.com', 'peacocktv.com', 'supercell.com', 'microsoft.com', 
                           'wikipedia.org', 'lufthansa.com', 'bloomberg.com', 'wordpress.org', 'epicgames.com', 'nibcdirect.nl', 'messenger.com', 'medicibank.nl', 'thestreet.com', 'eredivisie.nl', 'buienradar.nl', 'pinterest.com', 'crazyshit.com', 
                           'yachtlease.nl', 'eur.shein.com', 'buienalarm.nl', 'mediamarkt.nl', 'videoland.com', 'airfrance.com', 'investors.com', 'volkskrant.nl', 'parrotsec.org', 'mcdonalds.com', 'topbloemen.nl', 'wordpress.com', 'investing.com', 
                           'aljazeera.com', 'ziggosport.nl', 'ambcrypto.com', 'weeronline.nl', 'kaspersky.com', 'guardian.com', 'engadget.com', 'ubereats.com', 'eharmony.com', 'rtlnieuws.nl', 'gymshark.com', 'nl.gymshark.com', 'regiobank.nl', 'fidelity.com', 
                           'facebook.com', 'drive.google', 'outlook.live', 'coinbase.com', 'coinmerce.io', 'nintendo.com', 'emirates.com', 'coindesk.com', 'btcdirect.eu', 'acunetix.com', 'mashable.com', 'barchart.com', 'theverge.com', 
                           'decathlon.nl', 'utorrent.com', 'kaspersky.nl', 'buzzfeed.com', 'snapchat.com', 'airfrance.nl', 'tipranks.com', 'mcdonalds.nl', 'bitfinex.com', 'whatsapp.com', 'nl.shein.com', 'usatoday.com', 'groningen.nl', 
                           'huffpost.com', 'telegraaf.nl', 'tv.apple.com', 'linkedin.com', 'pringles.com', 'nintendo.nl', 'youtube.com', 'newsbtc.com', 'goflink.com', 'rabobank.nl', 'studygo.com', 'vulnweb.com', 'facebook.nl', 'discord.com', 
                           'bershka.com', 'bershka.nl', 'hallmark.nl', 'chatgpt.com', 'bitvavo.com', 'blogger.com', 'foxnews.com', 'alibaba.com', 'nytimes.com', 'gizmodo.com', 'coolblue.nl', 'schiphol.nl', 'okcupid.com', 'bitcoin.org', 'play.google', 
                           'vodafone.nl', 'archive.org', 'twitter.com', ' survio.com', 'bbcnews.com', 'rituals.com', 'melkunie.nl', 'news.google', 'abcnews.com', 'booking.com', 'spotify.com', 'cbsnews.com', 'redbull.com', 'meet.google', 
                           'weather.com', 'bestbuy.com', 'latimes.com', 'hsleiden.nl', 'anycoin.com', 'binance.com', 'overheid.nl', 'doritos.com', 'bittrex.com', 'reuters.com', 'netflix.com', 'dropbox.com', 'bitcoin.nl', 'finviz.com', 
                           'gemini.com', 'clover.com', 'utwente.nl', 'grindr.com', 'reddit.com', 'vandale.nl', 'schwab.com', 'google.com', 'apnews.com', 'doritos.nl', 'ziggogo.tv', 'abnamro.nl', 'target.com', 'zillow.com', 'bngbank.nl', 
                           'yandex.com', 'snsbank.nl', 'openai.com', 'login.live', 'flickr.com', 'ledger.com', 'moneyou.nl', 'blokker.nl', 'action.com', 'etrade.com', 'bigbank.nl', 'office.com', 'amazon.com', 'kraken.com', 'hbomax.com', 
                           'tiktok.com', 'boston.com', 'tudelft.nl', 'zalando.nl', 'triodos.nl', 'paypal.com', 'offsec.com', 'airbnb.com', 'wehkamp.nl', 'medium.com', 'synnex.com', 'etihad.com', 'kucoin.com', 'crypto.com', 'tinder.com', 
                           'tumblr.com', 'bumble.com', 'asnbank.nl', 'decrypt.co', 'github.com', 'voetbal.nl', 'minecraft.net', 'litebit.eu', 'forbes.com', 'redbull.nl', 'lynxtp.com', 'wechat.com', 'deezer.com', 'encyclo.nl', 'tmobile.nl', 'albert.nl', 
                           'fontys.nl', 'praxis.nl', 'badoo.com', 'postnl.nl', 'baidu.com', 'udemy.com', 'giphy.com', 'mango.com', 'skype.com', 'tenor.com', 'greetz.nl', 'denon.com', 'tvgids.nl', 'imgur.com', 'ana.co.jp', 'vinted.nl', 
                           'happn.com', 'zacks.com', 'fundap.nl', 'amazon.nl', 'conrad.nl', 'webmd.com', 'jdate.com', 'adobe.com', 'slack.com', 'apple.com', 'swiss.com', 'degiro.nl', 'tinder.nl', 'hinge.com', 'arriva.nl', 'twitch.tv', 
                           'slate.com', 'jumbo.com', 'yahoo.com', 'wired.com', 'zoosk.com', 'google.nl', 'nlziet.nl', 'viber.com', 'amazon.de', 'huobi.com', 'quora.com', 'indeed.nl', 'match.com', 'intel.com', 'cnbc.com', 'temu.com', 
                           'uber.com', 'digid.nl', 'ebay.com', 'xbox.com', 'aybl.com', 'imdb.com', 'phys.org', 'ncaa.com', 'vice.com', 'qbuzz.nl', 'bing.com', 'noaa.gov', 'gamma.nl', 'espn.com', 'time.com', 'hanze.nl', 'hulu.com', 
                           'kali.org', 'cnet.com', 'trouw.nl', 'avans.nl', 'ally.com', 'etsy.com', 'nmap.org', 'icbcs.nl', 'pathé.nl', 'lays.com', 'dell.com', 'ohpen.nl', 'zoom.us', 'mlb.com', 'espn.nl', 'kpn.com', 'ans.app', 'mms.com', 
                           'nyaa.si', 'nhl.com', 'kik.com', 'nibc.nl', 'hema.nl', 'rtlz.nl', 'nba.com', 'ebay.nl', '9292.nl', 'npr.org', 'dell.nl', 'vox.com', 'knab.nl', 'nfl.com', 'bbc.com', 'lays.nl', 'pof.com', 'wsj.com', 'bol.com', 'line.me', 
                           'ccn.com', 'cnn.com', 'avg.com', 'rug.nl', 'npo.nl', 'ing.nl', 'wur.nl', 'nos.nl', 'tui.nl', 'rtl.nl', 'han.nl', 'jbl.nl', 'uva.nl', 'eur.nl', 'hva.nl', 'nrc.nl', 'klm.nl', 'ah.nl', 'ou.nl', 'fd.nl', 'nu.nl', 'ru.nl', 
                           'x.com', 'uu.nl', 'ns.nl', 'hu.nl', 'vu.nl', 'ad.nl', 'de.nl', 'douglas.nl', 'iciparisxl.nl', 'web.whatsapp.com',
                           ]

applications = ['industrialandcommercialbankofchinalimited', 'nationale-nederlandenbank', 'garantibankinternational', 'medicibankinternational', 'microsoftauthenticator', 'yapikredibanknederland', 'nationale-nederlanden', 
                'loyalty-app.jumbo.com', 'deutschebanknederland', 'nationalenederlanden', 'hofhoornemanbankiers', 'westlandutrechtbank', 'vanlanschotbankiers', 'shadowofthecolossus', 'reddeadredemption', 'hofhoornemanohpen', 
                'oranjeinvestments', 'popcorntimeonline', 'vanlanschotkempen', 'translate.google', 'sonicthehedgehog', 'whatsappbusiness', 'easportspornhub', 'hanzehogeschool', 'christianmingle', 'merriam-webster', 'leagueoflegends', 
                'constantcontact', 'campaignmonitor', 'clevelandclinic', 'supermariomaker', 'dpboss.services', 'worldofwarcraft', 'tulphypotheken', 'demir-halkbank', 'assassinscreed', 'jetpackjoyride', 'activecampaign', 'candycrushsaga', 
                'crashbandicoot', 'microsoftteams', 'subwayservers', 'battlegrounds', 'subwaysurfers', 'counterstrike', 'seatsandsofas', 'handelsbanken', 'rijksoverheid', 'monsterhunter', 'streetfighter', 'frieslandbank', 'eightballpool', 
                'leaseplanbank', 'hollandcasino', 'playstation4', 'clickfunnels', 'thuisbezorgd', 'rocketleague', 'deutschebank', 'nintendoland', 'playstation5', 'finalfantasy', 'steampowered', 'elitesingles', 'clashofclans', 'residentevil', 
                'needforspeed', 'mijnoverheid', 'espncricinfo', 'civilization', 'mobilemonkey', 'mortalcombat', 'telefoonboek', 'tripadvisor', 'accuweather', 'hubspotchat', 'albertheijn', 'medlineplus', 'vanlanschot', 'squarespace', 
                'gotomeeting', 'amazonprime', ' tunnelbear', 'thedivision', 'woocommerce', 'starcitizen', 'playstation', 'thelastofus', 'brawl.stars', 'apexlegends', 'abnamrobank', 'popcorntime', 'clashroyale', 'getresponse', 'bigcommerce', 
                'marktplaats', 'monopoly go', 'monutatrust', 'innercircle', 'crunchyroll', 'speeleiland', 'hearthstone', 'triodosbank', 'candycrush', 'wetransfer', 'convertkit', 'googlehome', 'expressvpn', 'primevideo', 'mayoclinic', 
                'cyberghost', 'mailerlite', 'foursquare', 'royalmatch', 'buienalarm', 'thewitcher', 'streamyard', 'googlemaps', 'indiatimes', 'dyinglight', 'supermario', 'britannica', 'salesforce', 'friendster', 'callofduty', 'mail.yahoo', 
                'rainbowsix', 'nibcdirect', 'prestashop', 'brawlstars', 'trustpilot', 'yachtlease', 'videoprime', 'healthline', 'disneyplus', 'blackboard', 'googlemeet', 'windscribe', 'tombraider', 'sendinblue', 'mailchimp', 'supercell', 
                'wikipedia', 'starcraft', '8ballpool', 'leaseplan', 'titanfall', 'speedtest', 'instapage', 'justdance', 'teamspeak', 'leadpages', 'sparkpost', 'autopilot', 'minecraft', 'darksouls', 'spiderman', 'appear.in', 'theleague', 
                'tokopedia', 'protonvpn', 'peacocktv', 'pinduoduo', 'mariokart', 'massffect', 'microsoft', 'uncharted', 'jiocinema', 'watchdogs', 'freshdesk', 'regiobank', 'pinterest', 'decathlon', 'surfshark', 'instagram', 'cambridge', 
                'metalgear', 'sofascore', 'wordpress', 'steamapps', 'saintsrow', 'obsstudio', 'messenger', 'overwatch', 'helpscout', 'halfbrick', 'smashbros', 'chatfuel', 'eharmony', 'warframe', ' thefork', 'snapchat', 'linkedin', 'ubereats', 
                'facebook', 'rabobank', 'whatsapp', 'knabbank', 'monopoly', 'volusion', 'unbounce', ' vyprvpn', 'telltale', 'studygo', 'frontapp', 'ilovepdf', 'savefrom', 'godofwar', 'livechat', 'groovehq', 'intercom', 'hurriyet', 'flipkart', 'ventrilo', 
                'hangouts', 'valorant', 'opencart', 'terraria', 'xhamster', 'nibcbank', 'ludoking', 'telegram', 'fortnite', 'overheid', 'manychat', 'steamapp', 'moneyou', 'outlook', 'magento', 'appletv', 'hubspot', 'walmart', 'ingbank', 
                'triodos', 'madmimi', 'twitter', 'dumpert', 'webflow', 'landbot', 'nordvpn', 'blogger', 'discord', 'asnbank', 'disney+', 'moosend', 'snsbank', 'samsung', 'oneteam', 'jetpack', 'joyride', 'zalando', 'rakuten', 'spotify', 
                'philips', 'phonepe', 'fallout', 'destiny', 'xvideos', 'zendesk', 'witcher', 'outlast', 'netflix', 'goflink', 'abnamro', 'join.me', 'myspace', 'viaplay', 'android', 'peacock', 'chatgpt', 'shopify', 'booking', 'hay-day', 
                'nytimes', 'mailgun', 'klaviyo', 'hay.day', 'bngbank', 'amongus', 'blokker', 'xboxone', 'bigbank', 'mailjet', 'okcupid', 'pokemon', 'youtube', 'weather', 'xbox360', 'hbomax', 'nubank', 'paypal', 'clover', 'capcut', 'alipay', 
                'reddit', 'deusex', 'twitch', 'sekiro', 'spboss', 'adidas', 'rayman', 'signal', 'drupal', 'xsplit', 'meetup', 'vinted', 'safari', 'wechat', 'indeed', 'medium', 'joomla', 'weebly', 'hayday', 'douyin', 'amazon', 'yandex', 
                'tekken', 'icloud', 'grindr', 'roblox', 'aweber', 'google', 'airbnb', 'tumblr', 'openai', 'disney', 'bumble', 'sunweb', 'tiktok', 'tagged', 'mumble', 'fandom', 'deezer', 'tinder', 'taobao', 'meesho', 'limbo', 'webex', 'globo', 
                'denon', 'happn', 'slack', 'jumbo', 'shein', 'skype', 'hinge', 'orkut', 'vimeo', 'tesco', 'nba2k', 'viber', 'jitsi', 'flink', 'udemy', 'steam', 'linux', 'zelda', 'simyo', 'giphy', 'funda', 'ziggo', 'adobe', 'gmail', 'forza', 
                'drift', 'tele2', 'odido', 'teams', 'prime', 'badoo', 'yahoo', 'zoosk', 'hanze', 'tenor', 'quora', 'icbcs', 'crisp', 'jdate', 'canva', 'gamma', 'spele', 'temu', 'ikea', 'halo', 'drip', 'etsy', 'tawk', 'fifa', 'waze', 'pubg', 
                'hulu', 'zoho', 'bebo', 'dota', 'doom', 'sims', '9292', 'knab', 'emma', 'ebay', 'xbox', 'imdb', 'espn', 'uber', 'nibc', 'yelp', 'rabo', 'nike', 'bershka', 'douglas', 'loavies', 'iciparisxl', 'gymshark', 'kruidvat', 'whatsappweb',
                
                ]

# DICTIONARIES: 
discovered_hosts = {}
active_dict = {}
inactive_dict = {}
active_spoofing_threads = {}

# LISTS: 
skip_display_mac_address = []

# PARAMETERS
COUNTDOWN_TIMER = 25

# FLASK
app = Flask(__name__)
app.secret_key = 'Secret_Sniffer_Key_Ayo'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///athena.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Hosts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mac_address = db.Column(db.String(17), unique=True, nullable=True)
    ip_address = db.Column(db.String(15), unique=True, nullable=True)  # Assuming IPv4 addresses
    vendor = db.Column(db.String(255), nullable=True)  # Adjust the length as per your requirement
    hostname = db.Column(db.String(255), nullable=True)  # Adjust the length as per your requirement
    custom_name = db.Column(db.String(100), nullable=True)
    logs = db.relationship('Log', backref='device', lazy=True)



class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    log_message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now()) 
    host_id = db.Column(db.Integer, db.ForeignKey('hosts.id'), nullable=False)

with app.app_context():
    db.create_all()

# THREADING LOCKS
sniffer_running_lock = threading.Lock()
active_dict_lock = threading.Lock()
inactive_dict_lock = threading.Lock()

# OTHER
sniffer_running = False
sniffer_thread = None
selected_interface = None


###################################################################################################
##### VISUAL ######################################################################################
###################################################################################################

plus_sign = "[+]"
minus_sing = "[-]"
question_sign = "[?]"
warning_sign = "[!]"

###################################################################################################
##### FLASK ROUTES ################################################################################
###################################################################################################

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
    global host_machine_mac_address
    global selected_interface
    if request.method == 'POST':
        selected_interface = request.form.get('interface')
        host_machine_mac_address = get_mac_address(selected_interface)
        return render_template("index.html", interface=selected_interface, sniffer_running=sniffer_running, discovered_hosts=discovered_hosts)
    else:
        # Handle the case where the user directly accesses the /dashboard route
        return redirect(url_for('selecting_available_interface'))


@app.route('/start_stop_sniffer', methods=['POST'])
def start_stop_sniffer():
    global sniffer_running, sniffer_thread, selected_interface
    
    with sniffer_running_lock:
        sniffer_running = not sniffer_running
        
    if sniffer_running:
        if not sniffer_thread or not sniffer_thread.is_alive():
            if selected_interface:
                sniffer_thread = threading.Thread(target=sniff_network, args=(selected_interface,))
                sniffer_thread.start()
                print(f"{plus_sign} Sniffer started on interface:", selected_interface)
            else:
                print(f"{minus_sing} No interface selected. Cannot start sniffer.")
                return render_template('/choose_network_adapter.html')
        else:
            print(f"{plus_sign} Sniffer thread is already running.")
    else:
        if sniffer_thread and sniffer_thread.is_alive():
            sniffer_running = False  
            sniffer_thread.join()  
            print(f"{plus_sign} Sniffer stopped")
        else:
            print(f"{warning_sign} Sniffer thread is not running.")
            return render_template('/choose_network_adapter.html')
    
    return jsonify({'sniffer_running': sniffer_running})


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
    sorted_host_information = sorted(active_dict.items())
    
    for key, value in sorted_host_information:
        mac_address, website_or_application = key
        if mac_address not in skip_display_mac_address:
            matching_icons = find_matching_icons(website_or_application)
            icon_url = matching_icons[0] if matching_icons else None 
            website_or_application_visits = value['website_or_application_visit_counter']
            key = {'mac_address': mac_address, 'website_or_application_or_app': website_or_application, 'times_visited': website_or_application_visits, 'icon_url': icon_url}
            dict_to_send[str((mac_address, website_or_application))] = key
    
    return jsonify({'host_information': dict_to_send, 'skip_display_mac_address': skip_display_mac_address})


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


@app.route('/host_details', methods=['GET'])
def host_details():
    host_id = request.args.get('id')  
    if host_id is not None and host_id.isdigit():
        host_id = int(host_id)
        host_info = discovered_hosts.get(host_id) 
        if host_info:
            return render_template('host_details.html', host_info=host_info)  
    return render_template('host_not_found.html'), 404  




@app.route('/grab_host', methods=['POST'])
def grab_host():
    host_id = request.json.get('host_id')
    ip_address = request.json.get('ip_address')
    mac_address = request.json.get('mac_address')
    gateway_ip = '192.168.2.254'
    try:
        # Check if there's already a thread running for the IP address
        if ip_address in active_spoofing_threads:
            print(f"{minus_sing} Thread already active for {ip_address}. Skipping...")
            return jsonify({'message': f'Thread already active for {ip_address}. Skipping...'})

        thread = threading.Thread(target=run_arpspoof, args=(ip_address, gateway_ip, selected_interface)) 
        thread.start()
        print(f"{plus_sign} Threading started, Spoofing IP: {ip_address}")

        # Store the thread reference in the dictionary
        active_spoofing_threads[ip_address] = thread
        
        return jsonify({'message': f'Host {host_id} Grabbed.', 'ip_address': ip_address, 'mac_address': mac_address})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/stop_grab_host', methods=['POST'])
def stop_grab_host():
    ip_address = request.json.get('ip_address')
    try:
        # Check if there's an active thread for the IP address
        if ip_address in active_spoofing_threads:
            # Retrieve the thread from the dictionary
            thread = active_spoofing_threads[ip_address]
            # Terminate the thread
            thread.terminate()
            # Remove the thread reference from the dictionary
            del active_spoofing_threads[ip_address]
            print(f"Stopped ARP spoofing for {ip_address}")
            stop_sniffing()  # Stop sniffing for the IP address
            return jsonify({'message': f'Stopped ARP spoofing for {ip_address}'})
        else:
            return jsonify({'message': f'No active ARP spoofing for {ip_address} to stop'})
    except Exception as e:
        return jsonify({'error': str(e)})



# Route voor het 'killen' van een host
@app.route('/kill_host', methods=['POST'])
def kill_host():
    host_id = request.json.get('host_id')  # Haal het host_id op uit het POST-verzoek
    ip_address = request.json.get('ip_address')
    mac_address = request.json.get('mac_address')
    return jsonify({'message': f'Host {host_id} Killed.', 'ip_address': ip_address, 'mac_address': mac_address})



###################################################################################################
##### FUNCTIONS ###################################################################################
###################################################################################################

def sniff_network(interface):
    global sniffer_running
    print(f"{plus_sign} Sniffer thread started")
    while sniffer_running:
        print(sniffer_running)
        try:
            scapy.sniff(iface=interface, store=False, prn=sniffed_packet)
        except Exception as e:
            print(f"{minus_sing} An error occurred while sniffing packets:", e)
            traceback.print_exc()
    print(f"{minus_sing} Sniffer stopped")


def get_mac_address(interface=None):
    try:
        if interface:
            result = subprocess.check_output(["ifconfig", interface]).decode("utf-8")
        else:
            result = subprocess.check_output(["ifconfig"]).decode("utf-8")
            
        mac_address_search = re.search(r"([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}", result)
        if mac_address_search:
            mac_address = mac_address_search.group(0).lower()
            return mac_address
        else:
            return "MAC address not found for interface {}".format(interface)
    except subprocess.CalledProcessError:
        return "Error: Unable to get MAC address for interface {}".format(interface)

# Function to remove a host from the active_dict after a certain duration
def remove_host(host):
    # print(f"Started timer to remove Host with MAC address {host['mac_address']} for website_or_application: {host['website_or_application_visited']} after {duration} seconds.")
    while host['timer_counter'] > 0:
        # print(f"Countdown: {host['timer_counter']} seconds remaining for Host {host['mac_address']} for website_or_application: {host['website_or_application_visited']}.")
        time.sleep(1)
        with active_dict_lock:
            host['timer_counter'] -= 1
    with active_dict_lock:
        if (host['mac_address'], host['website_or_application_visited']) in active_dict:
            with inactive_dict_lock:
                inactive_dict[(host['mac_address'], host['website_or_application_visited'])] = host
                del active_dict[(host['mac_address'], host['website_or_application_visited'])]
                # print(f"Moved Host with MAC address {host['mac_address']} for website_or_application: {host['website_or_application_visited']} from active_dict to inactive_dict.")

# Function to add a host to the active_dict
def add_host_to_active_dict(mac_address, website_or_application):
    with active_dict_lock:
        if (mac_address, website_or_application) in active_dict:
            active_dict[(mac_address, website_or_application)]['timer_counter'] = COUNTDOWN_TIMER
            active_dict[(mac_address, website_or_application)]['website_or_application_visit_counter'] += 1
            print(f"Reset timer for Host with MAC address {mac_address} for website_or_application: {website_or_application} to 10 seconds. website_or_application times visited: {active_dict[(mac_address, website_or_application)]['website_or_application_visit_counter']}")
        else:
            host = {
                'mac_address': mac_address,
                'website_or_application_visited': website_or_application,
                'timer_counter': COUNTDOWN_TIMER,
                'website_or_application_visit_counter': 1
            }
            active_dict[(mac_address, website_or_application)] = host
            print(f"Added Host with MAC address {mac_address} for website_or_application: {website_or_application} to the active_dict.")
            threading.Thread(target=remove_host, args=(host,)).start()



def get_hostnames(ip_address):
    def get_hostname_by_dns(ip_address):
        try:
            hostname, _, _ = socket.gethostbyaddr(ip_address)
            return [hostname]
        except socket.herror:
            return []
        except socket.gaierror as e:
            print(f"{minus_sing} Error resolving hostname for {ip_address}: {e}")
            hostname = None 

    def get_hostname_by_reverse_dns(ip_address):
        try:
            _, _, hostnames = socket.gethostbyaddr(ip_address)
            return hostnames
        except socket.herror:
            return []
        except socket.gaierror as e:
            print(f"{minus_sing} Error resolving hostname for {ip_address}: {e}")
            hostname = None 

    # Try DNS lookup
    hostnames = get_hostname_by_dns(ip_address)

    if not hostnames:
        # If DNS lookup didn't return anything, try reverse DNS lookup
        hostnames = get_hostname_by_reverse_dns(ip_address)

    return hostnames

import csv

def get_vendor_from_mac(mac_address):
    try:
        macvendorsfile = r'gui/macvendors/mac-vendors-export.csv'
        macvendorsfile_second = r'macvendors/mac-vendors-export.csv'
        
        # Try opening the first file path
        try:
            with open(macvendorsfile, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                mac_address = mac_address.upper()
                mac = mac_address[:8]
                for row in csv_reader:
                    if mac == row['Mac Prefix']:
                        return row['Vendor Name']
        except FileNotFoundError:
            pass
        
        # If the first file path fails, try the second one
        try:
            with open(macvendorsfile_second, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                mac_address = mac_address.upper()
                mac = mac_address[:8]
                for row in csv_reader:
                    if mac == row['Mac Prefix']:
                        return row['Vendor Name']
        except FileNotFoundError:
            pass
        
        # If both file paths fail, return an empty string
        return ""
    
    except Exception as e:
        # Handle other exceptions if necessary
        print("An error occurred:", e)
        return None


def add_host_to_database(mac_address, ip_address, vendor, hostname):
    with app.app_context():
        existing_host = None
        
        if ip_address:
            # If IP address is provided, check if the host exists based on IP address
            existing_host = Hosts.query.filter_by(ip_address=ip_address).first()
            if existing_host:
                # If host exists based on IP address, update MAC address only if it's not present
                if existing_host.mac_address is None and mac_address:
                    existing_host.mac_address = mac_address
                db.session.commit()
                return "MAC address updated successfully."
        
        if mac_address:
            # If MAC address is provided or updated, check if the host exists based on MAC address
            existing_host = Hosts.query.filter_by(mac_address=mac_address).first()

        if existing_host:
            # If host exists based on MAC address, update other fields if they are not present
            if existing_host.ip_address is None and ip_address:
                existing_host.ip_address = ip_address
            if existing_host.vendor is None and vendor:
                existing_host.vendor = vendor
            if existing_host.hostname is None and hostname:
                existing_host.hostname = hostname
            db.session.commit()
            return "Host information updated successfully."
        else:
            # If no existing host found, add the new host to the database
            new_host = Hosts(mac_address=mac_address, ip_address=ip_address, vendor=vendor, hostname=hostname)
            db.session.add(new_host)
            db.session.commit()
            return "Host added successfully."





def add_host_to_discover_dict(ip_address, mac_address):
    import ipaddress
    
    # Define a function to check if an IP address is in the private range
    def is_private_ip(ip):
        private_ranges = [
            ("10.0.0.0", "10.255.255.255"),
            ("172.16.0.0", "172.31.255.255"),
            ("192.168.0.0", "192.168.255.255"),
        ]
        for start, end in private_ranges:
            if ipaddress.ip_address(ip) in ipaddress.ip_network(f"{start}/16"):
                return True
        return False
    
    # Check if the IP address / MAC address already exists in discovered_hosts
    for host_id, host_info in discovered_hosts.items():
        if host_info["ip_address"] == ip_address:
            if not host_info["mac_address"] or (mac_address and host_info["mac_address"] == mac_address):
                # Update MAC address if it's missing or if it has useful data
                discovered_hosts[host_id]["mac_address"] = mac_address
                return
            else:
                return
        elif host_info["mac_address"] == mac_address:
            if not host_info["ip_address"]:
                # Update IP address if it's missing
                discovered_hosts[host_id]["ip_address"] = ip_address
                # Update hostname if an IP is found for a host with existing MAC but no IP
                hostnames = get_hostnames(ip_address)
                if hostnames:
                    discovered_hosts[host_id]["hostname"] = hostnames[0]
            return
    
    # If the IP address doesn't exist, add a new host only if it's None or in private range
    if ip_address is None or is_private_ip(ip_address):
        host_id = len(discovered_hosts) + 1
        vendor = get_vendor_from_mac(mac_address)
        hostname = "" 
        
        if ip_address is not None:
            hostnames = get_hostnames(ip_address)
            if hostnames:
                hostname = hostnames[0]

        host_info = {   
            "mac_address": mac_address,
            "ip_address": ip_address,
            "vendor": vendor, 
            "hostname": hostname,
            "do_not_display": False,
        }
        discovered_hosts[host_id] = host_info
        with app.app_context():
            add_host_to_database(mac_address, ip_address, vendor, hostname)



def check_used_application(string_from_packet, src_mac, dst_mac):
    not_useful_data = ["googlecast", "googleapis", "googlezone", "pki-g", 'mijnmodem.kpn.home']
    
    try:
        if isinstance(string_from_packet, bytes):
            # Decode bytes to string using an appropriate encoding
            string_from_packet = string_from_packet.decode('utf-8')
        elif isinstance(string_from_packet, list):
            # Join list elements into a single string
            string_from_packet = ' '.join(map(str, string_from_packet))
        
        skip_processing = False
        for not_useful in not_useful_data: 
            if not_useful in string_from_packet.lower():
                skip_processing = True
                break

        if not skip_processing:
            for website_or_application in website_or_applications:
                if website_or_application in string_from_packet.lower():
                    add_host_to_active_dict(src_mac, website_or_application)
                    visited_website_or_application = f"www.{website_or_application}"
                    print(f"Visiting website_or_application: {visited_website_or_application:<20} | MAC SRC: {src_mac:<30} | MAC DST: {dst_mac:<40}")
                    break


    except Exception as e:
        print(f"{minus_sing} An error has occurred while trying to guess the used application or website_or_application: {e}")
        traceback.print_exc()

def get_used_application_from_raw_packet(packet, src_mac, dst_mac):
    # Check if the packet is sent by your own MAC address
    substrings_to_check = ["safari", "user-agent", "filename=google.png", "SERVER: Linux", '"website_or_application_or_app": "google"', '"icon_url": "static/icon_folder/google.png"', "'google\\'", '"vendor": "Google, Inc."', '"vendor": "Google', 'Visiting website_or_application: www.google.com']
    if src_mac == str(host_machine_mac_address) and "google" in packet.lower():
        return
    payload = packet.load.decode('utf-8', errors='ignore').lower()  # Convert to lowercase
    if any(substring in payload for substring in substrings_to_check):
        return

    for app in applications:
        if len(app) >= 4:
            if app.lower() in payload:  # Compare in lowercase
                print(f"Visiting Application: {app:<20} | MAC SRC: {src_mac:<30} | MAC DST: {dst_mac:<40}")
                print("-" * 50)
                add_host_to_active_dict(src_mac, app)



def sniffed_packet(packet):
    if packet:
        try:
            sniffed_packet_ethernet_src = None 
            sniffed_packet_ethernet_dst = None
            if packet.haslayer("Ethernet"):
                sniffed_packet_ethernet_src = packet["Ethernet"].src
                sniffed_packet_ethernet_dst = packet["Ethernet"].dst

            sniffed_packet_ip_src = None
            sniffed_packet_ip_dst = None
            if packet.haslayer("IP"):
                sniffed_packet_ip_src = packet["IP"].src
                sniffed_packet_ip_dst = packet["IP"].dst
            if packet.haslayer("DNS"):
                dns = packet.getlayer("DNS")
                # If there is an qd section in the DNS field
                if dns.qd:
                    qname = dns.qd.qname
                    if isinstance(qname, bytes):
                        qname = qname.decode('utf-8')
                    if qname:
                        check_used_application(qname, sniffed_packet_ethernet_src, sniffed_packet_ethernet_dst)

                # If there is an an section in the DNS field
                if dns.an:
                    for ans in dns.an:
                        rrname = ans.rrname
                        # check if instance is bytes, if it is convert to string utf-8
                        if isinstance(rrname, bytes):
                            rrname = rrname.decode('utf-8')
                        if rrname:
                            check_used_application(rrname, sniffed_packet_ethernet_src, sniffed_packet_ethernet_dst)

                        rdata = ans.rdata
                        # check if instance is bytes, if it is convert to string utf-8
                        if isinstance(rdata, bytes):
                            rdata = rdata.decode('utf-8')
                        if rdata:
                            check_used_application(rdata, sniffed_packet_ethernet_src, sniffed_packet_ethernet_dst)

            if packet.haslayer("Raw"):
                raw = packet.getlayer("Raw")
                if isinstance(raw, bytes):
                        raw = raw.decode('utf-8')
                get_used_application_from_raw_packet(packet, sniffed_packet_ethernet_src, sniffed_packet_ethernet_dst)

            add_host_to_discover_dict(sniffed_packet_ip_src, sniffed_packet_ethernet_src)

        except AttributeError:
            pass
        except Exception as e:
            print(f"{minus_sing} An error has occured while trying to sniff a packet!\n\n{e}\n")
            traceback.print_exc()

def extract_domain(url):
    extracted = tldextract.extract(url)
    domain = extracted.domain if extracted.domain else None
    return domain

import os

def find_matching_icons(input_website_or_application):
    icons_folder = "gui/static/icon_folder/"
    fallback_icons_folder = "static/icon_folder"
    
    try:
        icons = os.listdir(icons_folder)
    except FileNotFoundError:
        icons_folder = fallback_icons_folder
        icons = os.listdir(icons_folder)
    
    matching_icons = []
    icons_folder = "static/icon_folder/"
    domain = extract_domain(input_website_or_application)
    if domain:
        input_website_or_application = domain
    
    # First, look for an exact match
    for icon in icons:
        # Remove the file extension
        icon_name = os.path.splitext(icon)[0]
        
        # Check if the website_or_application name exactly matches the icon name
        if input_website_or_application == icon_name:
            matching_icons.append(os.path.join(icons_folder, icon))
            return matching_icons
    
    # If no exact match is found, look for partial matches
    for icon in icons:
        # Remove the file extension
        icon_name = os.path.splitext(icon)[0]
        
        # Check if the website_or_application name is contained in the icon name
        if input_website_or_application in icon_name:
            matching_icons.append(os.path.join(icons_folder, icon))
    
    if not matching_icons:
        matching_icons.append(os.path.join(icons_folder, "gray_picture_if_none_found.jpeg"))
    
    return matching_icons

if __name__ == "__main__":
    # Check if the script is being run with sudo
    if os.geteuid() != 0:
        print("This script requires elevated privileges. Please run it with sudo.")
        sys.exit(1)
    app.run(host='0.0.0.0', debug=True)
