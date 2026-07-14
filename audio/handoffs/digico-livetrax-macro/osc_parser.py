"""
OSC packet decoder used to reverse-engineer the DiGiCo Q225 <-> LiveTrax 3
exchange. Point it at a raw UDP payload (bytes) pulled from a pcap/pcapng
via scapy. Reusable for any future capture on this project.

Usage:
    from scapy.all import rdpcap, UDP, IP
    pkts = rdpcap("reference-capture_request-names-exchange.pcapng")
    for p in pkts:
        if UDP in p and p[UDP].payload:
            data = bytes(p[UDP].payload)
            print(parse_osc(data))
"""
import struct


def parse_osc(data: bytes):
    """Decode a single OSC packet: address, type tag string, args."""
    end = data.index(b'\x00')
    addr = data[:end].decode('ascii', errors='replace')
    pos = ((end + 4) // 4) * 4

    if pos >= len(data) or data[pos:pos + 1] != b',':
        # No type tag -- address-only message (e.g. heartbeat /strip/list)
        return addr, None, []

    tend = data.index(b'\x00', pos)
    typetag = data[pos:tend].decode('ascii', errors='replace')
    pos = ((tend + 4) // 4) * 4

    args = []
    for t in typetag[1:]:
        if t == 's':
            send = data.index(b'\x00', pos)
            s = data[pos:send].decode('ascii', errors='replace')
            args.append(s)
            pos = ((send + 4) // 4) * 4
        elif t == 'i':
            val = struct.unpack('>i', data[pos:pos + 4])[0]
            args.append(val)
            pos += 4
        elif t == 'f':
            val = struct.unpack('>f', data[pos:pos + 4])[0]
            args.append(val)
            pos += 4
        else:
            args.append(f"<unhandled type {t}>")

    return addr, typetag, args
