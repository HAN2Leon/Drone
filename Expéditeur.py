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
ADDR = b"Drone"       # Adresse d’émission

# --- Initialisation du module radio ---
pi = pigpio.pi()                                 # Connexion au démon pigpio
print("[VERIF] pigpio.connected:", getattr(pi, "connected", None))  # [VRF]

radio = NRF24(pi, ce=CE_PIN, spi_channel=SPI_CHANNEL, spi_speed=SPI_SPEED, channel=CHANNEL)
print("[VERIF] Objet NRF24 créé.")  # [VRF]

radio.open_writing_pipe(ADDR)                 # Ouvre le canal d’émission
print("[VERIF] Pipe émission configuré:", ADDR)  # [VRF]

print("NRF24 prêt. Entrez un message à envoyer :")

# --- Boucle principale : émission ---
while True:
    # Lecture du texte depuis le terminal
    text = input("Texte > ")
    number = int(input("Nombre (int) > "))
    flag = input("Booléen (true/false) > ").strip().lower() in ("true","1","yes","y","vrai","oui")

    payload = json.dumps({"text": text, "number": number, "flag": flag}, ensure_ascii=False).encode("utf-8")
    print("[VERIF] Saisie utilisateur:", payload, "| longueur:", len(payload))  # [VRF]
    print("[VERIF] Préparation à l’envoi…")  # [VRF]
    radio.send(payload)                          # Envoi direct du texte  
    print("[VERIF] Envoyé:", {"text": text, "number": number, "flag": flag})  # [VRF]