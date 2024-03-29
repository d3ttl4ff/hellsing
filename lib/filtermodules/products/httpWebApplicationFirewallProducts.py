import re

class WAFDetectionResults:
    def __init__(self):
        self.results = []

    def add_or_update(self, vendor, waf, blocked_categories=None):
        for entry in self.results:
            if entry['vendor'] == vendor:
                entry['waf'].add(waf)  # Assuming waf can be multiple per vendor, use a set to avoid duplicates
                if blocked_categories:
                    entry['blocked_categories'] = blocked_categories
                return
        # If no existing vendor is found, add a new entry
        self.results.append({
            'vendor': vendor,
            'waf': {waf},  # Use a set for potential multiple WAFs per vendor
            'blocked_categories': blocked_categories or "Not Available"
        })

class httpWebApplicationFirewallProducts:
    def __init__(self):
        self.waf_patterns = self._generate_waf_patterns()

    def _generate_waf_patterns(self):
        # Base pattern for WAF detection
        
        base_pattern = r'The site https?://.* is behind {} WAF\.'
        
        waf_names = {
            'aeSecure/aeSecure': 'aeSecure \(aeSecure\)',
            'Phion/Ergon/Airlock': 'Airlock \(Phion/Ergon\)',
            'Alert Logic/Alert Logic': 'Alert Logic \(Alert Logic\)',
            'Alibaba Cloud Computing/AliYunDun': 'AliYunDun \(Alibaba Cloud Computing\)',
            'Anquanbao/Anquanbao' : 'Anquanbao \(Anquanbao\)',
            'AnYu Technologies/AnYu': 'AnYu \(AnYu Technologies\)',
            'Approach/Approach': 'Approach \(Approach\)',
            'Armor/Armor Defense': 'Armor Defense \(Armor\)',
            'Microsoft/ASP.NET Generic Protection': 'ASP.NET Generic Protection \(Microsoft\)',
            'Czar Securities/Astra Web Protection': 'Astra Web Protection \(Czar Securities\)',
            'Amazon/AWS Elastic Load Balancer': 'AWS Elastic Load Balancer \(Amazon\)',
            'Baidu Cloud Computing/Yunjiasu': 'Yunjiasu \(Baidu Cloud Computing\)',
            'Ethic Ninja/Barikode': 'Barikode \(Ethic Ninja\)',
            'Barracuda Networks/Barracuda Application Firewall': 'Barracuda Application Firewall \(Barracuda Networks\)',
            'Faydata Technologies Inc./Bekchy': 'Bekchy \(Faydata Technologies Inc\.\)',
            'BinarySec/BinarySec': 'BinarySec \(BinarySec\)',
            'BitNinja/BitNinja': 'BitNinja \(BitNinja\)',
            'BlockDoS/BlockDoS': 'BlockDoS \(BlockDoS\)',
            'Bluedon IST/Bluedon': 'Bluedon \(Bluedon IST\)',
            'Varnish/CacheWall': 'CacheWall \(Varnish\)',
            'CdnNs/WdidcNet/CdnNS Application Gateway': 'CdnNS Application Gateway \(CdnNs/WdidcNet\)',
            'Cerber Tech/WP Cerber Security': 'WP Cerber Security \(Cerber Tech\)',
            'ChinaCache/ChinaCache CDN Load Balancer': 'ChinaCache CDN Load Balancer \(ChinaCache\)',
            'Yunaq/Chuang Yu Shield': 'Chuang Yu Shield \(Yunaq\)',
            'Cisco/ACE XML Gateway': 'ACE XML Gateway \(Cisco\)',
            'Penta Security/Cloudbric': 'Cloudbric \(Penta Security\)',
            'Cloudflare Inc./Cloudflare': 'Cloudflare \(Cloudflare Inc\.\)',
            'Amazon/Cloudfront': 'Cloudfront \(Amazon\)',
            'Comodo CyberSecurity/Comodo cWatch': 'Comodo cWatch \(Comodo CyberSecurity\)',
            'Jean-Denis Brun/CrawlProtect': 'CrawlProtect \(Jean-Denis Brun\)',
            'Rohde & Schwarz CyberSecurity/DenyALL': 'DenyALL \(Rohde & Schwarz CyberSecurity\)',
            'Distil Networks/Distil': 'Distil \(Distil Networks\)',
            'DOSarrest Internet Security/DOSarrest': 'DOSarrest \(DOSarrest Internet Security\)',
            'Applicure Technologies/DotDefender': 'DotDefender \(Applicure Technologies\)',
            'DynamicWeb/DynamicWeb Injection Check': 'DynamicWeb Injection Check \(DynamicWeb\)',
            'Verizon Digital Media/Edgecast': 'Edgecast \(Verizon Digital Media\)',
            'EllisLab/Expression Engine': 'Expression Engine \(EllisLab\)',
            'F5 Networks/BIG-IP Access Policy Manager': 'BIG-IP Access Policy Manager \(F5 Networks\)',
            'F5 Networks/BIG-IP Application Security Manager': 'BIG-IP Application Security Manager \(F5 Networks\)',
            'F5 Networks/BIG-IP Local Traffic Manager': 'BIG-IP Local Traffic Manager \(F5 Networks\)',
            'F5 Networks/FirePass': 'FirePass \(F5 Networks\)',
            'F5 Networks/Trafficshield': 'Trafficshield \(F5 Networks\)',
            'Fortinet/FortiWeb': 'FortiWeb \(Fortinet\)',
            'GoDaddy/GoDaddy Website Protection': 'GoDaddy Website Protection \(GoDaddy\)',
            'Grey Wizard/Greywizard': 'Greywizard \(Grey Wizard\)',
            'Art of Defense/HyperGuard': 'HyperGuard \(Art of Defense\)',
            'IBM/DataPower': 'DataPower \(IBM\)',
            'CloudLinux/Imunify360': 'Imunify360 \(CloudLinux\)',
            'Imperva Inc./Incapsula': 'Incapsula \(Imperva Inc\.\)',
            'Instart Logic/Instart DX': 'Instart DX \(Instart Logic\)',
            'Microsoft/ISA Server': 'ISA Server \(Microsoft\)',
            'Janusec/Janusec Application Gateway': 'Janusec Application Gateway \(Janusec\)',
            'Jiasule/Jiasule': 'Jiasule \(Jiasule\)',
            'KnownSec/KS-WAF': 'KS-WAF \(KnownSec\)',
            'Akamai/Kona Site Defender': 'Kona Site Defender \(Akamai\)',
            'LiteSpeed Technologies/LiteSpeed Firewall': 'LiteSpeed Firewall \(LiteSpeed Technologies\)',
            'Inactiv/Malcare': 'Malcare \(Inactiv\)',
            'Mission Control/Mission Control Application Shield': 'Mission Control Application Shield \(Mission Control\)',
            'SpiderLabs/ModSecurity': 'ModSecurity \(SpiderLabs\)',
            'NBS Systems/NAXSI': 'NAXSI \(NBS Systems\)',
            'PentestIt/Nemesida': 'Nemesida \(PentestIt\)',
            'Barracuda Networks/NetContinuum': 'NetContinuum \(Barracuda Networks\)',
            'Citrix Systems/NetScaler AppFirewall': 'NetScaler AppFirewall \(Citrix Systems\)',
            'AdNovum/NevisProxy': 'NevisProxy \(AdNovum\)',
            'NewDefend/Newdefend': 'Newdefend \(NewDefend\)',
            'NexusGuard/NexusGuard Firewall': 'NexusGuard Firewall \(NexusGuard\)',
            'NinTechNet/NinjaFirewall': 'NinjaFirewall \(NinTechNet\)',
            'NSFocus Global Inc./NSFocus': 'NSFocus \(NSFocus Global Inc\.\)',
            'BlackBaud/OnMessage Shield': 'OnMessage Shield \(BlackBaud\)',
            'Palo Alto Networks/Palo Alto Next Gen Firewall': 'Palo Alto Next Gen Firewall \(Palo Alto Networks\)',
            'PerimeterX/PerimeterX': 'PerimeterX \(PerimeterX\)',
            'PowerCDN/PowerCDN': 'PowerCDN \(PowerCDN\)',
            'ArmorLogic/Profense': 'Profense \(ArmorLogic\)',
            'Radware/AppWall': 'AppWall \(Radware\)',
            'Reblaze/Reblaze': 'Reblaze \(Reblaze\)',
            'RSJoomla!/RSFirewall': 'RSFirewall \(RSJoomla\!\)',
            'Microsoft/ASP.NET RequestValidationMode': 'ASP.NET RequestValidationMode \(Microsoft\)',
            'Sabre/Sabre Firewall': 'Sabre Firewall \(Sabre\)',
            'Safe3/Safe3 Web Firewall': 'Safe3 Web Firewall \(Safe3\)',
            'SafeDog/Safedog': 'Safedog \(SafeDog\)',
            'Chaitin Tech./Safeline': 'Safeline \(Chaitin Tech\.\)',
            'SecuPress/SecuPress WordPress Security': 'SecuPress WordPress Security \(SecuPress\)',
            'United Security Providers/Secure Entry': 'Secure Entry \(United Security Providers\)',
            'BeyondTrust/eEye SecureIIS': 'eEye SecureIIS \(BeyondTrust\)',
            'Imperva Inc./SecureSphere': 'SecureSphere \(Imperva Inc\.\)',
            'Neusoft/SEnginx': 'SEnginx \(Neusoft\)',
            'One Dollar Plugin/Shield Security': 'Shield Security \(One Dollar Plugin\)',
            'SiteGround/SiteGround': 'SiteGround \(SiteGround\)',
            'Sakura Inc./SiteGuard': 'SiteGuard \(Sakura Inc\.\)',
            'TrueShield/Sitelock': 'Sitelock \(TrueShield\)',
            'Dell/SonicWall': 'SonicWall \(Dell\)',
            'Sophos/UTM Web Protection': 'UTM Web Protection \(Sophos\)',
            'Squarespace/Squarespace': 'Squarespace \(Squarespace\)',
            'StackPath/StackPath': 'StackPath \(StackPath\)',
            'Sucuri Inc./Sucuri CloudProxy': 'Sucuri CloudProxy \(Sucuri Inc\.\)',
            'Tencent Technologies/Tencent Cloud Firewall': 'Tencent Cloud Firewall \(Tencent Technologies\)',
            'Citrix Systems/Teros': 'Teros \(Citrix Systems\)',
            'TransIP/TransIP Web Firewall': 'TransIP Web Firewall \(TransIP\)',
            'iFinity/DotNetNuke/URLMaster SecurityCheck': 'URLMaster SecurityCheck \(iFinity/DotNetNuke\)',
            'Microsoft/URLScan': 'URLScan \(Microsoft\)',
            'OWASP/Varnish': 'Varnish \(OWASP\)',
            'VirusDie LLC/VirusDie': 'VirusDie \(VirusDie LLC\)',
            'Wallarm Inc./Wallarm': 'Wallarm \(Wallarm Inc\.\)',
            'WatchGuard Technologies/WatchGuard': 'WatchGuard \(WatchGuard Technologies\)',
            'WebARX Security Solutions/WebARX': 'WebARX \(WebARX Security Solutions\)',
            'AQTRONIX/WebKnight': 'WebKnight \(AQTRONIX\)',
            'IBM/WebSEAL': 'WebSEAL \(IBM\)',
            'WebTotem/WebTotem': 'WebTotem \(WebTotem\)',
            'Feedjit/Wordfence': 'Wordfence \(Feedjit\)',
            'WTS/WTS-WAF': 'WTS-WAF \(WTS\)',
            '360 Technologies/360WangZhanBao': '360WangZhanBao \(360 Technologies\)',
            'XLabs/XLabs Security WAF': 'XLabs Security WAF \(XLabs\)',
            'Yundun/Yundun': 'Yundun \(Yundun\)',
            'Yunsuo/Yunsuo': 'Yunsuo \(Yunsuo\)',
            'Zenedge/Zenedge': 'Zenedge \(Zenedge\)',
            'Accenture/ZScaler': 'ZScaler \(Accenture\)',
            'West263 Content Delivery Network': 'West263 Content Delivery Network',
            'pkSecurity Intrusion Detection System': 'pkSecurity Intrusion Detection System',
            'Xuanwudun': 'Xuanwudun',
            'Open-Resty Lua Nginx WAF': 'Open-Resty Lua Nginx WAF',
        }

        waf_patterns = {}
        
        for waf_name, readable_format in waf_names.items():
            pattern = base_pattern.format(readable_format)

            waf_patterns[waf_name] = re.compile(pattern, re.IGNORECASE)

        return waf_patterns

    def parse_wafw00f_output(self, output):
        detected_wafs = []
        
        for waf_name, pattern in self.waf_patterns.items():
            if pattern.search(output):
                vendor, waf = waf_name.split('/', 1)
                detected_wafs.append({'vendor': vendor, 'waf': waf})

        return detected_wafs
    
    def parse_identywaf_output(self, output):
        # Extracting WAFs and vendors
        waf_pattern = re.compile(r'\[\+\] non-blind match: \'([^\']+)\'')
        wafs = waf_pattern.findall(output)

        # Structuring WAF and Vendor data
        waf_data = [{'vendor': waf.split(' (')[1][:-1], 'waf': waf.split(' (')[0]} for waf in wafs]

        # Extracting Blocked Categories
        blocked_categories_pattern = re.compile(r'\[\=\] blocked categories: ([^\n]+)')
        blocked_categories_matches = blocked_categories_pattern.search(output)
        blocked_categories = blocked_categories_matches.group(1) if blocked_categories_matches else "Could not detect."

        return waf_data, blocked_categories