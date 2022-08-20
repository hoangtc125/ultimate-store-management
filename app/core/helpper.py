from python_arptable import get_arp_table


def mac_from_ip(ip):
    arp_table = get_arp_table()
    for entry in arp_table:
        if entry['IP address'] == ip:
            return entry['HW address']
    return None
