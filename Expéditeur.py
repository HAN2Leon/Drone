import pigpio
import time
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
    message = input("Envoyer > ")                # Lecture du texte depuis le terminal
    print("[VERIF] Saisie utilisateur:", message, "| longueur:", len(message))  # [VRF]
    print("[VERIF] Préparation à l’envoi…")  # [VRF]
    
    radio.send(message)                          # Envoi direct du texte
    print("[VERIF] Envoi demandé à la radio.")  # [VRF]

    print("Envoyé :", message)