#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###
### Utils > NetworkUtils
###
import socket
import ipaddress
import time

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
