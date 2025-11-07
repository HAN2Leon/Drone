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
    i1 = True
    i2 = True
    flag2_prev = False
    t = 0
    while True:
        try:
            time.sleep(0.001)                              # Petite pause pour laisser le module traiter
            if (time.monotonic()-t) > 0.1:
                pi.write(27, False)
            while nRF24.data_ready():                    # Vérifie s’il y a des données entrantes
                t = time.monotonic()
                payload = nRF24.get_payload()            # Récupère le message reçu (sous forme de bytes)
                time_interval, seq, flag1, flag2, text_bytes = struct.unpack("<dI??18s",payload)
                text = text_bytes.rstrip(b'\x00').decode("utf-8")
                if i1 and flag1:
                    pi.write(17, flag1) 
                    i1 = False

                if flag2 != flag2_prev:
                    pi.write(27, flag2)
                flag2_prev = flag2
                print("Seq : ", seq) # Affiche le texte reçu
                #print(" | Time_interval : ", time_interval) 
                print(" | Flag1 : ", flag1) 
                print(" | Flag2 : ", flag2)
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
    flag1 = False
    flag2 = False
    text = get_message_input()
    time_interval = 0.0
    payload = bytearray(struct.pack("<dI??18s", time_interval, seq, flag1, flag2, text.encode("utf-8")))
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
    flag1 = False
    flag2 = False
    flag1_prev = False
    flag2_prev = False
    flag1_now = bool(pi.read(17))
    flag2_now = bool(pi.read(27))
    i1 = True
    i2 = True
    print("Transmition started.")
    while True:
        try:
            t0 = time.monotonic()

            flag1_now = bool(pi.read(17))
            if i1 and (not flag1_prev) and flag1_now:
                flag1 = flag1_now
                i1 = False
            flag1_prev = flag1_now

            flag2_now = bool(pi.read(27))
            if i2 and (not flag2_prev) and flag2_now:
                flag2 = flag2_now
                i2 = False
            if not i2 :
                flag2 = flag2_now
            flag2_prev = flag2_now

            payload[0:14] = struct.pack("<dI??", time_interval, seq, flag1, flag2)
            try:
                nRF24.send(payload)
                nRF24.wait_until_sent()
                print("Seq : ", seq) # Affiche le texte reçu
                #print(" | Time_interval : ", time_interval) 
                print(" | Flag1 : ", flag1) 
                print(" | Flag1 : ", flag2)
                print(" | Text : ", text) 
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