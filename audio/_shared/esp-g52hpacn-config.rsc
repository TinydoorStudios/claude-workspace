# MikroTik G-52HPacn — ESP (Elm Street Plaza)
# SSID: ChickenWing | WPA2 | 192.168.200.0/24 | AP mgmt IP .1 | DHCP server on AP
# Radio is 5GHz-only (Atheros AR9888) — no 2.4GHz hardware on this unit.
# Apply via Winbox/Terminal: import file=esp-g52hpacn-config.rsc (after copying to device)

# --- Bridge setup ---
/interface bridge
add name=bridgeLocal

/interface bridge port
add bridge=bridgeLocal interface=ether1
add bridge=bridgeLocal interface=wlan1

# --- Management IP ---
/ip address
add address=192.168.200.1/24 interface=bridgeLocal network=192.168.200.0

# --- DHCP Server ---
/ip pool
add name=dhcp_pool0 ranges=192.168.200.10-192.168.200.254

/ip dhcp-server
add address-pool=dhcp_pool0 interface=bridgeLocal name=dhcp1 lease-time=1d disabled=no

/ip dhcp-server network
add address=192.168.200.0/24 gateway=192.168.200.1 dns-server=8.8.8.8,1.1.1.1

# --- Wireless: 5GHz (only band this radio supports) ---
/interface wireless security-profiles
add name=ChickenWing-sec authentication-types=wpa2-psk mode=dynamic-keys wpa2-pre-shared-key=3cdc3cdc

/interface wireless
set wlan1 ssid=ChickenWing mode=ap-bridge band=5ghz-a/n/ac channel-width=20/40/80mhz-XXXX \
    security-profile=ChickenWing-sec wireless-protocol=802.11 disabled=no

# --- DNS (device itself resolving) ---
/ip dns
set servers=8.8.8.8,1.1.1.1 allow-remote-requests=yes

# --- Firewall / NAT left at RouterOS factory default (standard login, no lockdown requested) ---

# --- Identity ---
/system identity
set name=ESP-ChickenWing-AP
