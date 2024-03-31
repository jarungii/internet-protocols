import re
import socket
import subprocess
from ipwhois import IPWhois
from prettytable import PrettyTable


def tracing(domain, hops):
    try:
        ip = socket.gethostbyname(domain)
        print(f"Tracing route to {domain} [{ip}]")
        traceroute_output = subprocess.check_output(["tracert", "-h", str(hops), domain]).decode("cp1251")
        return traceroute_output
    except socket.gaierror:
        print("Hostname could not be resolved.")


def get_info(ip):
    try:
        who = IPWhois(ip)
        results = who.lookup_rdap()
        the_ip = results['query']
        as_info = results['asn']
        route_block = results['asn_cidr']
        country = results['asn_country_code']
        registry = results['asn_registry']
        the_results = (the_ip, as_info, route_block, country, registry)
        return the_results
    except Exception as e:
        return ip, " ", " ", " ", " "


def main():
    domains = input().split()
    hops = 10
    for domain in domains:
        table = PrettyTable()
        table.field_names = ["IP Address", "AS number", "AS route block", "AS country", "AS registry"]
        info = tracing(domain, hops)
        ipv4_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
        if info:
            for trace in info.split('\n'):
                ipv4_matches = re.search(ipv4_pattern, trace)
                if ipv4_matches:
                    row = get_info(ipv4_matches.group(0))
                    table.add_row(row)
                else:
                    continue
            print(table)


if __name__ == "__main__":
    main()

