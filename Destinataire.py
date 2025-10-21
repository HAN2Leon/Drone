import pigpio
import time
import json
import config.yaml
from nrf24 import NRF24

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# --- Adresses (à inverser sur l’autre module) ---
ADDR = config["addresses"]["ADDR"].encode()

# --- Initialisation du module radio ---
pi = pigpio.pi()                                 # Connexion au démon pigpio
print("[VERIF] pigpio.connected:", getattr(pi, "connected", None))  # [VRF]

radio = NRF24(
    pi,
    ce=config["radio"]["CE_PIN"],
    spi_channel=config["radio"]["SPI_CHANNEL"],
    spi_speed=config["radio"]["SPI_SPEED"],
    channel=config["radio"]["CHANNEL"],
    #payload_size=config["radio"]["payload_size"],
    #crc_bytes=config["radio"]["crc_bytes"],
)
print("[VERIF] Objet NRF24 créé.")  # [VRF]

radio.open_reading_pipe(1, ADDR)              # Ouvre le canal de réception (pipe 1)
print("[VERIF] Pipe réception (1) configuré:", ADDR)  # [VRF]

print("NRF24 prêt à recevoir")

# --- Boucle principale : réception ---
while True:
    time.sleep(0.1)                              # Petite pause pour laisser le module traiter
    recu = False  # [VRF]
    while radio.data_ready():                    # Vérifie s’il y a des données entrantes
        print("[VERIF] Données prêtes (data_ready=True).")  # [VRF]
        payload = radio.get_payload()            # Récupère le message reçu (sous forme de bytes)
        data = json.loads(bytes(payload).decode("utf-8"))
        print("[VERIF] Taille data:", len(data))  # [VRF]

        print("Reçu :", data) # Affiche le texte reçu
        recu = True  # [VRF]
    if not recu:  # [VRF]
        print("[RX] Aucune donnée prête pour le moment.")  # [VRF]