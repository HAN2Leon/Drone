import pigpio
import time
import json
from nrf24 import NRF24

# --- Configuration matérielle ---
CE_PIN = xx             # Broche CE du module nRF24L01
SPI_CHANNEL = 0          # Canal SPI principal (CE0)
SPI_SPEED = 100000        # Vitesse SPI (Hz)
CHANNEL = 76             # Canal radio (2400 + 76 MHz)

# --- Adresses (à inverser sur l’autre module) ---
ADDR = b"Drone"       # Adresse de réception

# --- Initialisation du module radio ---
pi = pigpio.pi()                                 # Connexion au démon pigpio
print("[VERIF] pigpio.connected:", getattr(pi, "connected", None))  # [VRF]

radio = NRF24(pi, ce=CE_PIN, spi_channel=SPI_CHANNEL, spi_speed=SPI_SPEED, channel=CHANNEL)
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