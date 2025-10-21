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