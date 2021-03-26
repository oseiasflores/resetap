
# Ferramenta para reset de APs na Jiga wisefi
# Discovery: Rodrigo Ramiro - rodrigo.ramiro@intebras.com.br
# Reset via API: Oséias Flores - oseias.flores@intelbras.com.br
# Alterou? Contribua! :)

import socket
import struct
import binascii
import time
from functools import reduce

MCAST_GRP = '233.89.188.1' 
MCAST_PORT = 10001
data_itb = struct.pack("BBBB", 0x49, 0x54, 0x42, 0x53)
data_dlb = struct.pack("BBBB", 0x00, 0x00, 0x00, 0x00)

def binaryToDevice(data):
        lst = []
        for ch in data:
            hv = hex(ch).replace('0x', '')
            if len(hv) == 1:
                hv = '0'+hv
            lst.append(hv)
            #print(lst)  
        pos = 0
        posEnd = 0
        tam = 0
        device = {}
        #print(device)
        #COD
        posEnd = 4+pos
        device['cod'] = reduce(lambda x,y:x+y, lst)[pos:posEnd]
        pos=posEnd
        
        #MAC Origem
        posEnd = 12+pos
        device['mac'] = reduce(lambda x,y:x+y, lst)[pos:posEnd]
        macFormat = ""
        for i in range(0,12,2):
            macFormat += device['mac'][i:i+2] + ":"
        device['mac'] = macFormat[:-1].upper()
        pos=posEnd

        #MAC destino
        posEnd = 12+pos
        device['mac_source'] = reduce(lambda x,y:x+y, lst)[pos:posEnd]
        macFormat = ""
        for i in range(0,12,2):
            macFormat += device['mac_source'][i:i+2] + ":"
        device['mac_source'] = macFormat[:-1].upper()
        pos=posEnd

        #Modelo
        posEnd = 4+pos
        tam = int(reduce(lambda x,y:x+y, lst)[pos:posEnd],16)*2
        pos=posEnd
            
        posEnd = tam+pos
        device['model'] = reduce(lambda x,y:x+y, lst)[pos:posEnd]
        device['model'] = bytes.fromhex(device['model']).decode('utf-8')
        #device['model'] = reduce(lambda x,y:x+y, lst)[pos:posEnd]
        pos=posEnd
        
        #Versao
        posEnd = 4+pos
        tam = int(reduce(lambda x,y:x+y, lst)[pos:posEnd],16)*2
        pos=posEnd
            
        posEnd = tam+pos
        device['version'] = reduce(lambda x,y:x+y, lst)[pos:posEnd]
        device['version'] = bytes.fromhex(device['version']).decode('utf-8')
        #device['version'] = reduce(lambda x,y:x+y, lst)[pos:posEnd]
        pos=posEnd
        
        #Porta
        posEnd = 4+pos
        device['port'] = int(reduce(lambda x,y:x+y, lst)[pos:posEnd],16)
        pos=posEnd
        
        #Description
        posEnd = 4+pos
        pos=posEnd
        
        posEnd = 16+pos
        device['description'] = reduce(lambda x,y:x+y, lst)[pos:posEnd]
        device['description'] = bytes.fromhex(device['description']).decode('utf-8')
        pos=posEnd
        
        return device

def resetapi(a, b):
  #Print modelo / IP
  print("\nIniciando processo de reset dos equipamentos!")
  print("Equipamentos que serão resetados ao padrão de fábrica: \n")
  for elem in b:
    print(f"Dut Model: {b}")
    for elem in a:
      print(f"IP: {a}\n")
  #Inicio tratamento requests
# Uma vez
def main():
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
  sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
  #sock.sendto(data_itb, (MCAST_GRP, MCAST_PORT))
  #sock.sendto(data_dlb, (MCAST_GRP, MCAST_PORT))
  # sock.setblocking(0)
  while True:
    try:
      apip = []
      apmodel = []
      print("Realizando Discovery de APs...\n")
      #Comentado envia o packet fora do laço (linha 99) envia apenas uma vez
      sock.sendto(data_itb, (MCAST_GRP, MCAST_PORT))
      data, address = sock.recvfrom(1024)
      #print ('received %s bytes from %s : %s' % (len(data), address, binaryToDevice(data)))
      takemodel = binaryToDevice(data)
      print (f'AP Encontrado: {address[0]} \nModel: {takemodel["model"]}!')
      apip.append(address[0])
      apmodel.append(takemodel['model'])
      while True:
        print("\nRealizar um novo discovery? \n")
        saidoloop = input("Utilize [s] ou [n]:")

        if saidoloop == 's' or saidoloop == 'S':
          break
        if saidoloop == 'n' or saidoloop == 'N':
          return resetapi(apip,apmodel)

        print("Opção Invalida! Utilize [s] ou [n]...")

    except socket.error:
      time.sleep(1)

main()
