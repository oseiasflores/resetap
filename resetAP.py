
# Ferramenta para reset de APs na Jiga wisefi
# Discovery: Rodrigo Ramiro - rodrigo.ramiro@intebras.com.br
# Reset via API: Oséias Flores - oseias.flores@intelbras.com.br
# Alterou? Contribua! :)

import socket
import struct
import binascii
import time
from functools import reduce
import requests
import json

MCAST_GRP = '233.89.188.1' 
MCAST_PORT = 10001
data_itb = struct.pack("BBBB", 0x49, 0x54, 0x42, 0x53)
data_dlb = struct.pack("BBBB", 0x00, 0x00, 0x00, 0x00)

login = """
{
    "data": {
    "username":'admin',
    "password":'lockzeus'
    }
}
"""
headers = {
  'Content-Type': 'application/json'
}

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
  i = 0
  p = 1
  #Print modelo / IP
  print("\nIniciando processo de reset dos equipamentos!")
  print("Equipamentos que serão resetados ao padrão de fábrica: \n")
  
  #Inicio tratamento requests
  for elem in a:
    urlbase ='http://'+a[i]+':80'
    #print(urlbase)
    print(f"{p}) DUT {a[i]}  | {b[i]}")

    response = requests.post(urlbase + '/cgi-bin/api/v3/system/login', data=login, headers=headers)
    sresponse = str(response)

    # Verificar se logou com sucesso no DUT
    if sresponse == '<Response [200]>':
        print("\nLOGIN EFETUADO COM SUCESSO!!!")
        state = True
    else:
        print("Falha no Login: {}".format(response))
        state = False

    if state == True:
        # Armazenar json response
        auth_token = response.json()

        # Filtrando apenas o value token e ajustando o token para uso no novo headers
        toke = auth_token.get('data')
        toke = toke.get('Token')
        tokef = 'Token ' + toke

        services = {
            'Authorization': tokef
        }

        print(f"\nRestaurando padrão de fábrica do DUT {p}")
        response = requests.delete(urlbase + '/cgi-bin/api/v3/system/config', headers=services)
        
        #Tratar exceptions aqui...  TO DO
        print("Sucesso!")
        
        #factory = response.json()
        #print(factory)
        
    else:
        print("Falha ao tentar resetar o DUT...\n")
        print("Tente novamente..\n")
        #menu()

    #Incrementador das listas de IP e Modelo    
    i = i + 1
    p = p + 1
    
# Uma vez
def main():
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
  sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
  sock.sendto(data_itb, (MCAST_GRP, MCAST_PORT))
  #sock.sendto(data_dlb, (MCAST_GRP, MCAST_PORT))
  # sock.setblocking(0)
  apip = []
  apmodel = []
  while True:
    sock.settimeout(1)
    try:
      print("Realizando Discovery de APs...\n")
      #Comentado envia o packet fora do laço (linha 99) envia apenas uma vez
      #sock.sendto(data_itb, (MCAST_GRP, MCAST_PORT))
      data, address = sock.recvfrom(1024)
      #print ('received %s bytes from %s : %s' % (len(data), address, binaryToDevice(data)))
      takemodel = binaryToDevice(data)
      print (f'AP Encontrado: {address[0]} \nModel: {takemodel["model"]}!')
      apip.append(address[0])
      apmodel.append(takemodel['model'])
      time.sleep(1)
   
    except socket.error or socket.timeout:
      print("Fim do Discover...\n")
      return resetapi(apip,apmodel)

      #time.sleep(1)

    #print("\nRealizar um novo discovery? \n")
    #saidoloop = input("Utilize [s] ou [n]:")

    #if saidoloop == 's' or saidoloop == 'S':
    #  
    #if saidoloop == 'n' or saidoloop == 'N':
    #  return resetapi(apip,apmodel)
    #
    #    print("Opção Invalida! Utilize [s] ou [n]...")
main()
