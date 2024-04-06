import tldextract
# import os

# def extract_domain(url):
#     extracted = tldextract.extract(url)
#     domain = extracted.domain if extracted.domain else None
#     return domain


# def find_matching_icons(input_website):
#     icons_folder = "gui/static/icon_folder/"
#     icons = os.listdir(icons_folder)
    
#     matching_icons = []
#     icons_folder = "static/icon_folder/"
#     domain = extract_domain(input_website)
#     if domain:
#         input_website = domain
    
#     # First, look for an exact match
#     for icon in icons:
#         # Remove the file extension
#         icon_name = os.path.splitext(icon)[0]
        
#         # Check if the website name exactly matches the icon name
#         if input_website == icon_name:
#             matching_icons.append(os.path.join(icons_folder, icon))
#             return matching_icons
    
#     # If no exact match is found, look for partial matches
#     for icon in icons:
#         # Remove the file extension
#         icon_name = os.path.splitext(icon)[0]
        
#         # Check if the website name is contained in the icon name
#         if input_website in icon_name:
#             matching_icons.append(os.path.join(icons_folder, icon))
    
#     if not matching_icons:
#         matching_icons.append(os.path.join(icons_folder, "gray_picture_if_none_found.jpeg"))
    
#     return matching_icons

# print(find_matching_icons("gemeente.groningen.nl"))


# dicttyyy = {
#     ('00:0c:29:3d:c3:b8', 'google'): {'website_times_visited': 1},
#     ('38:d8:2f:25:a9:a8', 'google'): {'website_times_visited': 1},
#     ('38:87:d5:34:c6:9b', 'spotify'): {'website_times_visited': 1},
#     ('00:05:cd:33:b1:e7', 'spotify'): {'website_times_visited': 1}
# }

# new_dict = {}

# for key, value in dicttyyy.items():
#     mac_address, website = key
#     website_visits = value['website_times_visited']
    
#     # Creating new keys in the desired format
#     new_key = {'mac_address': mac_address, 'website_or_app': website, 'times_visited': website_visits}
    
#     # Adding the new key-value pair to the new dictionary
#     new_dict[str(key)] = new_key

# print(new_dict)

# """
# arpspoof -i wlan0 -t 192.168.2.4 192.168.2.254
# arpspoof -i wlan0 -t 192.168.2.254 192.168.2.4
# """

# from scapy.all import *

# # Functie om pakketten te onderscheppen en te printen
# def intercept_packets(packet):
#     if packet.haslayer(Ether):  # Controleren op Ethernet-laag
#         src_mac = packet[Ether].src  # Bron MAC-adres
#         dst_mac = packet[Ether].dst  # Bestemmings-MAC-adres
#     else:
#         src_mac = dst_mac = None

#     if packet.haslayer(IP):
#         src_ip = packet[IP].src
#         dst_ip = packet[IP].dst
#         protocol = packet[IP].proto
#     else:
#         # Pakket heeft geen IP-laag, dus we slaan het over
#         return

#     # Controleren of het protocol TCP of UDP is
#     if protocol == 6 and packet.haslayer(TCP):
#         src_port = packet[TCP].sport
#         dst_port = packet[TCP].dport
#     elif protocol == 17 and packet.haslayer(UDP):
#         src_port = packet[UDP].sport
#         dst_port = packet[UDP].dport
#     else:
#         src_port = dst_port = None

#     populaire_apps = ['industrialandcommercialbankofchinalimited', 'nationale-nederlandenbank', 'garantibankinternational', 'medicibankinternational', 'yapikredibanknederland', 'microsoftauthenticator', 'nationale-nederlanden', 
#         'deutschebanknederland', 'nationalenederlanden', 'hofhoornemanbankiers', 'westlandutrechtbank', 'vanlanschotbankiers', 'vanlanschotkempen', 'popcorntimeonline', 'oranjeinvestments', 'hofhoornemanohpen', 'whatsappbusiness', 
#         'translate.google', 'merriam-webster', 'easportspornhub', 'dpboss.services', 'constantcontact', 'clevelandclinic', 'christianmingle', 'campaignmonitor', 'tulphypotheken', 'microsoftteams', 'jetpackjoyride', 'demir-halkbank', 
#         'candycrushsaga', 'activecampaign', 'subwaysurfers', 'subwayservers', 'seatsandsofas', 'rijksoverheid', 'leaseplanbank', 'handelsbanken', 'frieslandbank', 'eightballpool', 'telefoonboek', 'mobilemonkey', 'espncricinfo', 'elitesingles', 
#         'deutschebank', 'clickfunnels', 'clashofclans', 'woocommerce', 'vanlanschot', 'tripadvisor', 'triodosbank', 'squarespace', 'speeleiland', 'popcorntime', 'monutatrust', 'monopoly go', 'medlineplus', 'innercircle', 'hubspotchat', 
#         'gotomeeting', 'getresponse', 'crunchyroll', 'clashroyale', 'bigcommerce', 'amazonprime', 'albertheijn', 'accuweather', 'abnamrobank', ' tunnelbear', 'yachtlease', 'windscribe', 'wetransfer', 'videoprime', 'trustpilot', 'streamyard', 
#         'sendinblue', 'salesforce', 'royalmatch', 'primevideo', 'prestashop', 'nibcdirect', 'mayoclinic', 'mailerlite', 'mail.yahoo', 'indiatimes', 'healthline', 'googlemeet', 'googlemaps', 'googlehome', 'friendster', 'foursquare', 'expressvpn', 
#         'disneyplus', 'cyberghost', 'convertkit', 'candycrush', 'callofduty', 'britannica', 'blackboard', 'wordpress', 'wikipedia', 'tokopedia', 'theleague', 'teamspeak', 'surfshark', 'speedtest', 'sparkpost', 'sofascore', 'regiobank', 
#         'protonvpn', 'pinterest', 'pinduoduo', 'peacocktv', 'obsstudio', 'microsoft', 'messenger', 'mailchimp', 'leaseplan', 'leadpages', 'jiocinema', 'instapage', 'instagram', 'helpscout', 'freshdesk', 'decathlon', 'cambridge', 'autopilot', 
#         'appear.in', '8ballpool', 'xhamster', 'whatsapp', 'volusion', 'ventrilo', 'unbounce', 'telegram', 'snapchat', 'savefrom', 'rabobank', 'overheid', 'opencart', 'nibcbank', 'monopoly', 'manychat', 'ludoking', 'livechat', 'linkedin', 
#         'knabbank', 'intercom', 'ilovepdf', 'hurriyet', 'hangouts', 'groovehq', 'frontapp', 'fortnite', 'flipkart', 'facebook', 'eharmony', 'chatfuel', ' vyprvpn', ' thefork', 'zendesk', 'zalando', 'youtube', 'xvideos', 'webflow', 'weather', 
#         'walmart', 'viaplay', 'twitter', 'triodos', 'spotify', 'snsbank', 'shopify', 'samsung', 'rakuten', 'phonepe', 'peacock', 'outlook', 'okcupid', 'nytimes', 'nordvpn', 'netflix', 'myspace', 'moosend', 'moneyou', 'mailjet', 'mailgun', 
#         'magento', 'madmimi', 'landbot', 'klaviyo', 'join.me', 'jetpack', 'ingbank', 'hubspot', 'dumpert', 'disney+', 'discord', 'chatgpt', 'booking', 'bngbank', 'blokker', 'blogger', 'bigbank', 'asnbank', 'appletv', 'abnamro', 'yandex', 
#         'xsplit', 'weebly', 'wechat', 'vinted', 'twitch', 'tumblr', 'tinder', 'tiktok', 'taobao', 'tagged', 'sunweb', 'spboss', 'signal', 'safari', 'roblox', 'reddit', 'paypal', 'openai', 'nubank', 'mumble', 'meetup', 'meesho', 'medium', 
#         'joomla', 'indeed', 'icloud', 'hbomax', 'grindr', 'google', 'fandom', 'drupal', 'douyin', 'disney', 'deezer', 'clover', 'capcut', 'bumble', 'aweber', 'amazon', 'alipay', 'zoosk', 'ziggo', 'yahoo', 'webex', 'vimeo', 'viber', 'tesco', 
#         'tenor', 'tele2', 'teams', 'steam', 'spele', 'slack', 'skype', 'simyo', 'shein', 'quora', 'prime', 'orkut', 'odido', 'jitsi', 'jdate', 'icbcs', 'hinge', 'happn', 'hanze', 'gmail', 'globo', 'giphy', 'gamma', 'funda', 
#         'drift', 'crisp', 'canva', 'badoo', 'adobe', 'zoho', 'yelp', 'waze', 'uber', 'toto', 'temu', 'tawk', 'rabo', 'nike', 'nibc', 'line', 'knab', 'imdb', 'ikea', 'hulu', 'etsy', 'espn', 'emma', 'ebay', 'drip', 'bebo', 
#         'wix', 'uol', 'sns', 'pof', 'kpn', 'kik', 'bng', 'bbc', 'asn', 'xbox', 'xbox360', 'xboxone', 'playstation', 'playstation4', 'playstation5', 'supercell', 'clashroyale', 'clashofclans', 'marktplaats', 'halfbrick', 'jetpackjoyride',
#         'jetpack', 'joyride', 'brawlstars', 'hayday', 'hay-day', 'hay.day', 'brawl.stars', 'udemy', 'loyalty-app.jumbo.com', 'loyalty-app.jumbo.com', 'albertheijn', 'airbnb', "9292", 'oneteam', 'philips',
#         'android', 'linux', 'adidas', 'hanzehogeschool', 'mijnoverheid', 'hollandcasino', 'buienalarm']
    
#     if packet.haslayer(Raw):
#         payload = packet[Raw].load.decode('utf-8', errors='ignore').lower()  # Omzetten naar kleine letters
#         for app in populaire_apps:
#             if len(app) < 4:
#                 if app == "hbo":
#                     continue
#                 else:
#                     return
#             if app.lower() in payload:  # Vergelijken in kleine letters
#                 print(f"{app} gevonden in payload:")
#                 if src_mac:
#                     src_mac = src_mac
#                 else:
#                     src_mac = "NOTFOUND"
                
#                 if dst_mac:
#                     dst_mac = dst_mac
#                 else:
#                     dst_mac = "NOTFOUND"

#                 print(src_mac, dst_mac)
#                 # print("\n", payload, "\n")
#                 print("-" * 50)

# # Voorbeeldgebruik
# if __name__ == "__main__":
#     sniff(prn=intercept_packets)

applications = [
    'maastrichtuniversity.nl', 'ongediertebestrijden.nl', 'nationalgeographic.com', 'hogeschoolrotterdam.nl', 'interactivebrokers.com', 'vanlanschotkempen.com', 'universiteitleiden.nl', 'iknowwhatyoudownload.com',
    'tilburguniversity.edu', 'theweathernetwork.com', 'popcorntimeonline.xyz', 'outlook.office365.com', 'gemeente.groningen.nl', 'vanlanschotkempen.nl', 'oranjeinvestments.nl', 'thepiratebay.org',
    'mail.google.com/chat', 'www.google.com/maps', 'teams.microsoft.com', 'hangouts.google.com', 'christianmingle.com', 'calendar.google.com', 'businessinsider.com', 'turkishairlines.com', 
    'weatherchannel.com', 'washingtonpost.com', 'chicagotribune.com', 'bleacherreport.com', 'groningermuseum.nl', 'britishairways.com', 'cryptobriefing.com', 'tulphypotheken.nl', 'limetorrents.lol',
    'thedailybeast.com', 'stackoverflow.com', 'stackexchange.com', 'outlook.office365', 'independent.co.uk', 'demir-halkbank.nl', 'milieucentraal.nl', 'coinmarketcap.com', 'bittorrent.com',
    'cryptocompare.com', 'coinmarketcal.com', 'cointelegraph.com', 'yapikredibank.nl', 'yahooweather.com', 'wunderground.com', 'web.telegram.org', 'rijksoverheid.nl', 'outlook.live.com', 'teletekst.startpagina.nl',
    'mijn.overheid.nl', 'metoffice.gov.uk', 'leaseplanbank.nl', 'handelsbanken.nl', 'frieslandbank.nl', 'elitesingles.com', 'businessweek.com', 'bbcweather.co.uk', 'arstechnica.com', 'utorrent.com', 'mooistedorpjes.nl',
    'steampowered.com', 'qatarairways.com', 'singaporeair.com', 'tdameritrade.com', 'tradestation.com', 'investopedia.com', 'seekingalpha.com', 'bravenewcoin.com', 'cryptopotato.com', 'voetbalwedstrijdenvandaag.nl',
    'forexfactory.com', 'vvvnederland.nl', 'venturebeat.com', 'chat.openai.com', 'play.google.com', 'outlook.live.nl', 'news.google.com', 'mijnoverheid.nl', 'meet.google.com', 'innercircle.com', 'kickasstorrents.pw',
    'hofhoorneman.nl', 'google.com/chat', 'deutschebank.nl', 'crunchyroll.com', 'cntraveller.com', 'calendar.google', 'accuweather.com', 'playstation.com', 'marketaxess.com', 'drive.google.com', 'magnet-yify.com0',
    'prorealtime.com', 'stoneisland.com', 'theguardian.com', 'thinkorswim.com', 'marketwatch.com', 'tradingview.com', 'stockcharts.com', 'duckduckgo.com', 'vanlanschot.nl', '123movies.online', 'stadslyceum.nl',
    'techcrunch.com', 'starchannel.nl', 'primevideo.com', 'monutatrust.nl', 'marktplaats.nl', 'login.live.com', 'lifehacker.com', 'google.nl/maps', 'garantibank.nl', 'disneyplus.com', 'vandaaginside.nl',
    'consent.google', 'aolweather.com', 'aliexpress.com', 'torproject.org', 'nerdwallet.com', 'fcgroningen.nl', 'obsproject.com', 'ip-tracker.org', 'pathe-thuis.nl', 'stocktwits.com', 'ziggosport.nl', 'thuisbezorgd.nl',
    'motleyfool.com', 'blockchain.com', 'cryptonews.com', 'beincrypto.com', 'yachtlease.nl', 'wordpress.org', 'wikipedia.org', 'weeronline.nl', 'volkskrant.nl', 'topbloemen.nl', 'archive.org', 'new-123movies.live',
    'theleague.com', 'pinterest.com', 'peacocktv.com', 'parrotsec.org', 'nibcdirect.nl', 'newyorker.com', 'microsoft.com', 'messenger.com', 'medicibank.nl', 'mediamarkt.nl', 'pullandbear.com', 'vpnoverview.com',
    'instagram.com', 'crazyshit.com', 'buienradar.nl', 'buienalarm.nl', 'bloomberg.com', 'aljazeera.com', 'kaspersky.com', 'epicgames.com', 'mcdonalds.com', 'supercell.com', 'melkunie.nl', 'radioveronica.nl',
    'airfrance.com', 'lufthansa.com', 'videoland.com', 'wordpress.com', 'robinhood.com', 'investing.com', 'nl.shein.com', 'eur.shein.com', 'thestreet.com', 'ambcrypto.com', 'investors.com', 'whatsapp.com', 
    'usatoday.com', 'tv.apple.com', 'telegraaf.nl', 'airfrance.nl', 'snapchat.com', 'regiobank.nl', 'outlook.live', 'mashable.com', 'linkedin.com', 'huffpost.com', 'guardian.com', 'facebook.com', 'deezer.com',
    'engadget.com', 'eharmony.com', 'drive.google', 'decathlon.nl', 'buzzfeed.com', 'gymshark.com', 'nintendo.com', 'kaspersky.nl', 'pringles.com', 'groningen.nl', 'mcdonalds.nl', 'vice.com', 'studygo.com',
    'emirates.com', 'theverge.com', 'fidelity.com', 'barchart.com', 'tipranks.com', 'coinbase.com', 'coindesk.com', 'bitfinex.com', 'acunetix.com', 'coinmerce.io', 'btcdirect.eu', 'youtube.com', 
    'weather.com', 'vodafone.nl', 'twitter.com', 'spotify.com', 'reuters.com', 'rabobank.nl', 'play.google', 'overheid.nl', 'okcupid.com', 'nytimes.com', 'news.google', 'netflix.com', 'torrentz2.nz'
    'nbcnews.com', 'meet.google', 'latimes.com', 'hsleiden.nl', 'gizmodo.com', 'foxnews.com', 'discord.com', 'bershka.com', 'coolblue.nl', 'chatgpt.com', 'cbsnews.com', 'blogger.com', 'bestbuy.com', 'praxis.nl', 
    'bbcnews.com', 'abcnews.com', 'facebook.nl', ' survio.com', 'nintendo.nl', 'doritos.com', 'bitcoin.org', 'redbull.com', 'rituals.com', 'schiphol.nl', 'dropbox.com', 'alibaba.com', 'hallmark.nl',
    'booking.com', 'binance.com', 'bittrex.com', 'newsbtc.com', 'bitvavo.com', 'vulnweb.com', 'anycoin.com', 'ziggogo.tv', 'zalando.nl', 'yandex.com', 'wehkamp.nl', 'wechat.com', 'vandale.nl', 'voetbal.nl', 'eredivisie.nl',
    'utwente.nl', 'tumblr.com', 'tudelft.nl', 'triodos.nl', 'tmobile.nl', 'tinder.com', 'tiktok.com', 'target.com', 'snsbank.nl', 'reddit.com', 'paypal.com', 'openai.com', 'office.com', 'livesoccertv.com',
    'moneyou.nl', 'medium.com', 'login.live', 'hbomax.com', 'grindr.com', 'google.com', 'github.com', 'forbes.com', 'flickr.com', 'clover.com', 'bumble.com', 'boston.com', 'bngbank.nl', 'rtlnieuws.nl', 
    'blokker.nl', 'bigbank.nl', 'asnbank.nl', 'amazon.com', 'action.com', 'abnamro.nl', 'offsec.com', 'encyclo.nl', 'doritos.nl', 'redbull.nl', 'etihad.com', 'airbnb.com', 'zillow.com', 'uber.com', 'ubereats.com',
    'apnews.com', 'etrade.com', 'schwab.com', 'finviz.com', 'kraken.com', 'gemini.com', 'synnex.com', 'lynxtp.com', 'kucoin.com', 'crypto.com', 'ledger.com', 'decrypt.co', 'bitcoin.nl', 'litebit.eu', 'udemy.com', 
    'zoosk.com', 'yahoo.com', 'wired.com', 'vinted.nl', 'viber.com', 'twitch.tv', 'tvgids.nl', 'tenor.com', 'tinder.nl', 'slate.com', 'slack.com', 'skype.com', 'quora.com', 'postnl.nl', 'match.com', 'goflink.com',
    'jumbo.com', 'jdate.com', 'indeed.nl', 'imgur.com', 'hinge.com', 'happn.com', 'greetz.nl', 'google.nl', 'giphy.com', 'fundap.nl', 'fontys.nl', 'conrad.nl', 'baidu.com', 'badoo.com', 'espn.nl',
    'apple.com', 'amazon.nl', 'amazon.de', 'albert.nl', 'intel.com', 'degiro.nl', 'arriva.nl', 'mango.com', 'denon.com', 'ana.co.jp', 'swiss.com', 'nlziet.nl', 'adobe.com', 'webmd.com', 'nyaa.si',
    'zacks.com', 'huobi.com', 'trouw.nl', 'time.com', 'temu.com', 'phys.org', 'pathé.nl', 'ohpen.nl', 'noaa.gov', 'nmap.org', 'ncaa.com', 'kali.org', 'icbcs.nl', 'hulu.com', 'hanze.nl', 
    'gamma.nl', 'etsy.com', 'espn.com', 'ebay.com', 'digid.nl', 'cnet.com', 'cnbc.com', 'bing.com', 'avans.nl', 'aybl.com', 'xbox.com', 'lays.com', 'dell.com', 'qbuzz.nl', 'imdb.com', 
    'ally.com', 'zoom.us', 'wsj.com', 'vox.com', 'rtlz.nl', 'pof.com', 'npr.org', 'nibc.nl', 'nhl.com', 'nfl.com', 'nba.com', 'mlb.com', 'line.me', 'kpn.com', 'knab.nl', 'kik.com', 
    'hema.nl', 'ebay.nl', 'cnn.com', 'bol.com', 'bbc.com', 'ans.app', 'avg.com', 'lays.nl', 'mms.com', 'dell.nl', '9292.nl', 'ccn.com', 'wur.nl', 'uva.nl', 'rug.nl', 'rtl.nl', 'nrc.nl', 
    'npo.nl', 'nos.nl', 'ing.nl', 'hva.nl', 'han.nl', 'eur.nl', 'jbl.nl', 'klm.nl', 'tui.nl', 'x.com', 'vu.nl', 'uu.nl', 'ru.nl', 'ou.nl', 'nu.nl', 'hu.nl', 'fd.nl', 'de.nl', 'ah.nl', 
    'ad.nl', 'ns.nl']

# Verwijder duplicaten
unieke_games = list(set(applications))

# Sorteer de lijst op basis van lengte van de woorden (langste woord eerst)
gesorteerde_lijst = sorted(unieke_games, key=lambda x: len(x), reverse=True)

# Print de gesorteerde lijst
print(gesorteerde_lijst)