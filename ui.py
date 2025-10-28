import struct
from debug import try_to_run


@try_to_run
def get_message_input(): # Lecture du texte depuis le terminal
    text = input("Texte > ")
    number = int(input("Nombre (int) > "))
    flag = input("Booléen (true/false) > ").strip().lower() in ("true","1","yes","y","vrai","oui")
    print("[VERIF] Saisie utilisateur:", number, flag, text, "| longueur:", len(f"{number}{flag}{text}"))  # [VRF]
    return number, flag, text


@try_to_run
def form_message_payload(seq=None):
    number, flag, text = get_message_input()
    payload = bytearray(struct.pack("<HH?27s", seq, number, flag, text.encode("utf-8")))
    return payload
