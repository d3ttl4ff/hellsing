#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###
### Utils > NetworkUtils
###
import socket
import ipaddress
import time
from urllib.parse import urlparse
from lib.output.Logger import logger

class NetworkUtils:
    
    @staticmethod
    def dns_lookup(domain_name):
        """Resolve domain name to IP address."""
        try:
            return socket.gethostbyname(domain_name)
        except socket.gaierror:
            return None

    @staticmethod
    def reverse_dns_lookup(ip_address):
        """Resolve IP address to domain name."""
        try:
            return socket.gethostbyaddr(ip_address)[0]
        except socket.herror:
            return None
      
    @staticmethod  
    def is_valid_port(port):
        """Check if the provided string is a valid port number."""
        try:
            return 0 <= int(port) <= 65535
        except ValueError:
            return False
        
    @staticmethod
    def get_port_from_url(url):
        """Return port from URL"""
        parsed = urlparse(url)
        if parsed.port:
            return int(parsed.port)
        else:
            return 443 if parsed.scheme == 'https' else 80
        
    @staticmethod
    def extract_secondary_domain(domain):
        """
        Extracts the secondary domain and TLD from a given domain, excluding subdomains.
        This function does not handle edge cases like ccSLDs.
        """
        parts = domain.split('.')
        # Ensure the domain has at least two parts
        if len(parts) >= 2:
            # Return the last two parts of the domain (secondary domain and TLD)
            return '.'.join(parts[-2:])
        else:
            return domain
        
    # Check if a host is reachable by attempting to connect on a given port
    @staticmethod
    def is_host_reachable(ip_or_domain, port=80):
        """Check if a host is reachable by attempting to connect on a given port."""
        try:
            # Attempt to establish a socket connection
            socket.setdefaulttimeout(3)  # Timeout for the socket connection
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                if sock.connect_ex((ip_or_domain, port)) == 0:
                    return True  # The host is reachable
        except Exception as e:
            logger.error(f"Error checking reachability of {ip_or_domain}: {e}")
        return False  # The host is not reachable