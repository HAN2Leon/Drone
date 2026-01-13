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
    t = 0
    secu_prev = False
    gach_prev = False
    secu_now = False
    gach_now = False

    while True:
        try:
            time.sleep(0.001)                              # Petite pause pour laisser le module traiter
            if (time.monotonic()-t) > 0.1:
                motor_run_timed_secu(-1, 3, pi)
            while nRF24.data_ready():                    # Vérifie s’il y a des données entrantes
                t = time.monotonic()
                payload = nRF24.get_payload()            # Récupère le message reçu (sous forme de bytes)
                time_interval, seq, secu_now, gach_now = struct.unpack_from("<dI??", payload, 0) 

                if secu_now and (not secu_prev):
                    motor_run_timed_secu(1, 3, pi)

                if secu_prev and (not secu_now):
                    motor_run_timed_secu(-1, 3, pi)

                if secu_now and gach_now and (not gach_prev):
                    motor_run_timed_gach(1, 5, pi)
                    time.sleep(3000)
                    motor_run_timed_gach(-1, 5, pi)
                
                secu_prev = secu_now
                gach_prev = gach_now

                print("Seq : ", seq) # Affiche le texte reçu
                #print(" | Time_interval : ", time_interval) 
                print(" | Sécurité : ", secu_now) 
                print(" | Gachette : ", gach_now)
        except KeyboardInterrupt:
            print("Listening stopped.")
            break


PWM_SECU= 17   # PWM
DIR_SECU = 27  # DIR
SPEED_SECU = 60 # Rapport cyclique %
PWM_GACH = 19   # PWM
DIR_GACH = 26   # DIR
SPEED_GACH = 60 # Rapport cyclique %


def init_DRV8871(pi):
    pi.set_mode(PWM_SECU, pigpio.OUTPUT)
    pi.set_mode(DIR_SECU, pigpio.OUTPUT)

    pi.set_PWM_frequency(PWM_SECU, 1000)
    pi.set_PWM_dutycycle(PWM_SECU, 0)

    pi.set_mode(PWM_GACH, pigpio.OUTPUT)
    pi.set_mode(DIR_GACH, pigpio.OUTPUT)

    pi.set_PWM_frequency(PWM_GACH, 1000)
    pi.set_PWM_dutycycle(PWM_GACH, 0)


def motor_run_secu(dir, pi):
    pi.write(DIR_SECU, 0 if dir == 1 else 1)
    pi.set_PWM_dutycycle(PWM_SECU, int(SPEED_SECU * 255 / 100))


def motor_run_gach(dir, pi):
    pi.write(DIR_GACH, 0 if dir == 1 else 1)
    pi.set_PWM_dutycycle(PWM_GACH, int(SPEED_GACH * 255 / 100))


def motor_stop_secu(pi):
    pi.set_PWM_dutycycle(PWM_SECU, 0)


def motor_stop_gach(pi):
    pi.set_PWM_dutycycle(PWM_GACH, 0)


def motor_run_timed_secu(dir, t, pi):
    motor_run_secu(dir, pi)
    time.sleep(t)
    motor_stop_secu(pi)


def motor_run_timed_gach(dir, t, pi):
    motor_run_gach(dir, pi)
    time.sleep(t)
    motor_stop_gach(pi)


def main_interaction():
    nRF24, config, pi = init_nRF24() 
    nRF24.open_reading_pipe(0, config.get_address_ground_to_air())
    #!!!!!!!!!!!!!!!!!!!!!!!
    init_DRV8871(pi)
    start_reading(nRF24, pi)


if __name__ == "__main__" :
    main_interaction()