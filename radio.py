import pigpio # type: ignore
from nrf24 import NRF24
import configurator
import time
import struct
from debug import try_to_run


@try_to_run
def init_nRF24():
    config = configurator.get_config()
    pi = pigpio.pi()

    nRF24 = NRF24(
        pi,
        ce = config.get_ce_pin(),
        spi_channel = config.get_spi_channel(),
        spi_speed = config.get_spi_speed(),
        channel = config.get_channel(),
        payload_size = config.get_payload_size(),
        data_rate = config.get_data_rate(),
        pa_level = config.get_pa_level(),
        crc_bytes = config.get_crc_bytes())

    return nRF24, config, pi


@try_to_run
def start_reading(nRF24, pi):
    print("Listening started.")
    while True:
        try:
            time.sleep(0.001)                              # Petite pause pour laisser le module traiter
            while nRF24.data_ready():                    # Vérifie s’il y a des données entrantes
                payload = nRF24.get_payload()            # Récupère le message reçu (sous forme de bytes)
                time_interval, seq, flag, text_bytes = struct.unpack("<dI?19s",payload)
                text = text_bytes.rstrip(b'\x00').decode("utf-8")
                if flag:
                    pi.write(17, flag) 
                print("Seq : ", seq) # Affiche le texte reçu
                #print(" | Time_interval : ", time_interval) 
                print(" | Flag : ", flag) 
                print(" | Text : ", text) 
        except KeyboardInterrupt:
            print("Listening stopped.")
            break


@try_to_run
def get_message_input(): # Lecture du texte depuis le terminal
    text: str = input("Texte > ")
    print("[VERIF] Saisie utilisateur:", text)  # [VRF]
    return text


@try_to_run
def form_message_payload():
    seq = 0
    flag = False
    text = get_message_input()
    time_interval = 0.0
    payload = bytearray(struct.pack("<dI?19s", time_interval, seq, flag, text.encode("utf-8")))
    return payload, text


@try_to_run
def send_once(nRF24, config):
    payload = form_message_payload(config)
    try:
        nRF24.send(payload)
        nRF24.wait_until_sent()
    except:
        print(f"[ERREUR] Perte de liaison avec le drone — ACK manquant")


@try_to_run
def send_fixed_cycle(nRF24, peroid, pi):
    payload, text = form_message_payload()
    next_t = time.monotonic()
    time_interval = 0
    seq = 0
    flag = False
    print("Transmition started.")
    while True:
        try:
            t0 = time.monotonic()
            if bool(pi.read(17)):
                flag = True
            payload[0:13] = struct.pack("<dI?", time_interval, seq, flag)
            try:
                nRF24.send(payload)
                nRF24.wait_until_sent()
                print("Seq : ", seq, " | Interval : ", time_interval, " | Flag : ", flag, " | Text : ", text)
            except:
                print(f"[ERREUR] Perte de liaison avec le drone — ACK manquant")
            seq += 1
            next_t += peroid
            remaining = next_t - time.monotonic()
            if remaining > 0:
                time_interval = time.monotonic() - t0
                time.sleep(remaining)
            else:
                time_interval = time.monotonic() - t0
                next_t = time.monotonic()
        except KeyboardInterrupt:
            print("Transmition stopped.")
            break