import pigpio # type: ignore
from nrf24 import NRF24
import configurator
import time
import struct
from debug import try_to_run

PIN_SECU = 17
PIN_GACH = 27

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
def send_fixed_cycle(nRF24, peroid, pi):
    next_t = time.monotonic()
    time_interval = 0
    seq = 0
    secu = False
    gach = False
    secu_prev = False
    gach_prev = False
    secu_now = bool(pi.read(PIN_SECU))
    gach_now = bool(pi.read(PIN_GACH))
    i1 = True
    i2 = True
    print("Transmition started.")
    while True:
        try:
            t0 = time.monotonic()

            secu_now = bool(pi.read(PIN_SECU))
            if i1 and (not secu_prev) and secu_now:
                secu = secu_now
                i1 = False
            if not i1 :
                secu = secu_now
            secu_prev = secu_now

            gach_now = bool(pi.read(PIN_GACH))
            if i2 and (not gach_prev) and gach_now:
                gach = gach_now
                i2 = False
            if not i2 :
                gach = gach_now
            gach_prev = gach_now

            payload = bytearray(struct.pack("<dI??18s", time_interval, seq, secu, gach))
   
            try:
                nRF24.send(payload)
                nRF24.wait_until_sent()
                print("Seq : ", seq) # Affiche le texte reçu
                #print(" | Time_interval : ", time_interval) 
                print(" | Sécurité : ", secu) 
                print(" | Gachette : ", gach)
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


def main_interaction():
    nRF24, config, pi= init_nRF24()
    period = 0.01
    nRF24.open_writing_pipe(config.get_address_ground_to_air())
    #!!!!!!!!!!!!!!!!!!!!!!!
    send_fixed_cycle(nRF24, period, pi)


if __name__ == "__main__" :
    main_interaction()