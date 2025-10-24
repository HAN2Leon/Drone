import pigpio
import time
import struct
import yaml
from nrf24 import NRF24

try : 
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
except :
    print ("[ERROR] Failed to open .ymal")

# --- Adresses ---
try : 
    ADDR = config["addresses"]["ADDR"].encode()
except :
    print ("[ERROR] Addresses not found")

# --- Initialisation du module radio ---
try :
    pi = pigpio.pi()                                 # Connexion au démon pigpio
    print("[VERIF] pigpio.connected:", getattr(pi, "connected", None))  # [VRF]
except :
    print ("[ERROR] Failed to connect to pigpio")

try : 
    radio = NRF24(
        pi,
        ce=config["radio"]["CE_PIN"],
        spi_channel=config["radio"]["SPI_CHANNEL"],
        spi_speed=config["radio"]["SPI_SPEED"],
        channel=config["radio"]["CHANNEL"],
        #payload_size=config["radio"]["payload_size"],
        #crc_bytes=config["radio"]["crc_bytes"],
    )
    print("[VERIF] Objet nRF24 créé.")  # [VRF]
except :
    print ("[ERROR] Failed to initiate nRF24")

try :
    radio.open_reading_pipe(1, ADDR)              # Ouvre le canal de réception (pipe 1)
    print("[VERIF] Pipe réception (1) configuré:", ADDR)  # [VRF]
    print("NRF24 prêt à recevoir")
except :
    print ("[ERROR] Failed to open reading pipe")

# --- Boucle principale : réception ---

try :
    while True:
        time.sleep(0.1)                              # Petite pause pour laisser le module traiter
        recu = False  # [VRF]
        while radio.data_ready():                    # Vérifie s’il y a des données entrantes
            print("[VERIF] Données prêtes (data_ready=True).")  # [VRF]
            payload = radio.get_payload()            # Récupère le message reçu (sous forme de bytes)
            number,flag,text_bytes = struct.unpack("<H?28s",payload)
            text = text_bytes.rstrip(b'\x00').decode("utf-8")
            print("[VERIF] Taille data:", len(payload))  # [VRF]

            print("Reçu :\nNumber : ",number,"\nFlag : ",flag,"\nText : ",text ) # Affiche le texte reçu
            recu = True  # [VRF]
        #if not recu:  # [VRF]
            #print("[RX] Aucune donnée prête pour le moment.")  # [VRF]
except KeyboardInterrupt:
    print ("Stop listening")
except Exception as e:
    print ("[ERROR] Not listening.",e)
finally :
    try :
        pi.stop()
    except Exception :
        print("Failed to stop Pigpio")
        pass
    finally :
        print ("Programme is over.\nGoodbye !")
