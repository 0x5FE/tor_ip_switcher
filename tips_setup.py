#!/usr/bin/env python3
"""
Configuration tool for tor_ip_switcher /etc/tor/torrc
Usage: tips_setup.py <your_new_password>
By Rupe 08.21.2018, updated 11.09.2023
"""

import os
import subprocess
import sys
import time

TORRC_PATH = '/etc/tor/torrc'

def hash_password(password):
    hashed_password = subprocess.getoutput(f'tor --hash-password "{password}"').split()[-1]
    return hashed_password

def enable_control_port():
    try:
        with open(TORRC_PATH, 'a') as torrc:
            torrc.write("\nControlPort 9051\n")
            torrc.write(f"HashedControlPassword {ControlHashedPassword}\n")
        return True
    except Exception as e:
        print(f"Error enabling ControlPort: {e}")
        return False

def reload_tor_config():
    try:
        tor_pid = subprocess.getoutput('pidof tor')
        if tor_pid:
            subprocess.call(['kill', '-HUP', tor_pid])
            print("\n[✓] Tor Config: Reloaded")
            return True
        else:
            print("\n[✗] Tor Daemon: Not running")
            return False
    except Exception as e:
        print(f"Error reloading Tor config: {e}")
        return False

if __name__ == '__main__':
    if os.geteuid() != 0:
        sys.exit('Run as super user!')

    if len(sys.argv) != 2:
        sys.exit("\n[!] Usage: %s <your_new_password>\n" % os.path.basename(__file__))

    ControlHashedPassword = hash_password(sys.argv[1])

    try:
        print("\n[?] Gathering torrc config information [?]")
        
        if os.path.isfile(TORRC_PATH):
            with open(TORRC_PATH, 'r') as torrc:
                torrc_content = torrc.read()
                if 'HashedControlPassword' not in torrc_content:
                    if enable_control_port():
                        if reload_tor_config():
                            print(
                                " [✓] ControlPort 9051: Enabled\n",
                                " [✓] HashedControlPassword: Enabled\n",
                                " [✓] /etc/tor/torrc: Updated successfully\n",
                                " [✗] Password set to: ", sys.argv[1], "\n",
                                " [✗] HashedControlPassword ", ControlHashedPassword, "\n")
                    else:
                        sys.exit("\n[✗] Unable to enable ControlPort and HashedControlPassword\n")
                else:
                    print("\n[✓] ControlPort and HashedControlPassword already configured\n")
        else:
            sys.exit("\n[✗] /etc/tor/torrc missing\n")

    except Exception as err:
        print(err)
