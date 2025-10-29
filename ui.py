import struct
from debug import try_to_run


@try_to_run
def get_message_input(): # Lecture du texte depuis le terminal
    text: str = input("Texte > ")
    number: int = int(input("Nombre (int) > "))
    flag: bool = input("Booléen (true/false) > ").strip().lower() in ("true","1","yes","y","vrai","oui")
    print("[VERIF] Saisie utilisateur:", number, flag, text, "| longueur:", len(f"{number}{flag}{text}"))  # [VRF]
    return number, flag, text


@try_to_run
def form_message_payload(config, seq=0):
    number, flag, text = get_message_input()
    pa_level = config.get_pa_level()
    payload = bytearray(struct.pack("<HHH?25s", seq, pa_level, number, flag, text.encode("utf-8")))
    return payload
