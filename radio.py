import pigpio # type: ignore
from nrf24 import NRF24
import configurator
import time
import struct
import ui
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

    return nRF24, config



@try_to_run
def start_reading(nRF24):
    try:
        while True:
            time.sleep(0.01)                              # Petite pause pour laisser le module traiter
            while nRF24.data_ready():                    # Vérifie s’il y a des données entrantes
                payload = nRF24.get_payload()            # Récupère le message reçu (sous forme de bytes)
                number,flag,seq,text_bytes = struct.unpack("<H?H27s",payload)
                text = text_bytes.rstrip(b'\x00').decode("utf-8")
                print("Taille data:", len(payload), " | Number : ",number ," | Flag : ",flag ," | Seq : ",seq ," | Text : ",text ) # Affiche le texte reçu
    except KeyboardInterrupt:
        pass



@try_to_run
def send_once(nRF24):
    payload = ui.form_message_payload()
    ok = nRF24.send(payload)
    if not ok:
        print(f"[ERREUR] Perte de liaison avec le drone — ACK manquant")
    return ok



@try_to_run
def send_fixed_cycle(nRF24, payload, peroid):
    payload = ui.form_message_payload()
    seq = 0
    next_t = time.monotonic()
    try:
        while True:
            t0 = time.monotonic()
            payload[0:2] = struct.pack("<H", seq)
            ok = nRF24.send(payload)
            if not ok:
                print(f"[ERREUR] Perte de liaison avec le drone — ACK manquant, seq = {seq}")
            seq += 1
            next_t += peroid
            remaining = next_t - time.monotonic()
            if remaining > 0:
                time.sleep(remaining)
            else:
                next_t = time.monotonic()
    except KeyboardInterrupt:
        pass