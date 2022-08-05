import os
import json

import requests

# Reference: https://data.iana.org/rdap/dns.json
with open('assets/dns.json', 'r') as f:
    data = json.load(f)

services = data['services']

__all__ = ['whois']


def whois(domain: str):
    # Reference: https://www.rfc-editor.org/rfc/rfc7484.html
    domain_split = domain.split('.')
    domains = ['.'.join(domain_split[i:]) for i in range(len(domain_split))]
    for service in services:
        try:
            if any((dmn in service[0]) for dmn in domains):
                service_url = service[-1][-1]
                r = requests.get(os.path.join(service_url, 'domain/', domain))
                if r.status_code == 200 and r.json().get('ldhName'):
                    return r.json()
        except:
            pass

    return {}
