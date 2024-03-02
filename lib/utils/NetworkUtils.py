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
    def dns_lookup(host):
        """
        Get IP corresponding to a given hostname 
        Return the first IPv4 in the list of IPs if available, otherwise the first IPv6
        """
        ip_list = list()
        try:
            ip_list = list(set(str(i[4][0]) for i in socket.getaddrinfo(host, 80)))
        except:
            return None
        if len(ip_list) == 0:
            return None

        for ip in ip_list:
            if type(ipaddress.ip_address(ip)) == ipaddress.IPv4Address:
                return ip
        return ip_list[0]


    @staticmethod
    def reverse_dns_lookup(ip):
        """Get hostname from IP if reverse DNS entry exists"""
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return ip