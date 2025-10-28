#from __future__ import annotations
import yaml # type: ignore
from debug import try_to_run


@try_to_run
def open_yaml():
    with open("config.yaml", "r") as f:
        default_config = yaml.safe_load(f)
    return default_config

class configurations:
    def __init__(self,
                 ce_pin,
                 spi_channel,
                 spi_speed,
                 channel,
                 payload_size,
                 data_rate,
                 pa_level,
                 crc_bytes,
                 address_ground_to_air,
                 address_air_to_ground):
        
        self.__ce_pin = ce_pin
        self.__spi_channel = spi_channel
        self.__spi_speed = spi_speed
        self.__channel = channel
        self.__payload_size = payload_size
        self.__data_rate = data_rate
        self.__pa_level = pa_level
        self.__crc_bytes = crc_bytes
        self.__address_ground_to_air = address_ground_to_air
        self.__address_air_to_ground = address_air_to_ground

    def set_ce_pin(self, new_ce_pin):
        self.__ce_pin = new_ce_pin

    def get_ce_pin(self):
        return self.__ce_pin

    def set_spi_channel(self, new_spi_channel):
        self.__spi_channel = new_spi_channel

    def get_spi_channel(self):
        return self.__spi_channel

    def set_spi_speed(self, new_spi_speed):
        self.__spi_speed = new_spi_speed

    def get_spi_speed(self):
        return self.__spi_speed

    def set_channel(self, new_channel):
        self.__channel = new_channel

    def get_channel(self):
        return self.__channel

    def set_payload_size(self, new_payload_size):
        self.__payload_size = new_payload_size

    def get_payload_size(self):
        return self.__payload_size

    def set_data_rate(self, new_data_rate):
        self.__data_rate = new_data_rate

    def get_data_rate(self):
        return self.__data_rate

    def set_pa_level(self, new_pa_level):
        self.__pa_level = new_pa_level

    def get_pa_level(self):
        return self.__pa_level
    
    def set_crc_bytes(self, new_crc_bytes):
        self.__crc_bytes = new_crc_bytes

    def get_crc_bytes(self):
        return self.__crc_bytes

    def set_address_ground_to_air(self, new_address_ground_to_air):
        self.__address_ground_to_air = new_address_ground_to_air

    def get_address_ground_to_air(self):
        return self.__address_ground_to_air

    def set_address_air_to_ground(self, new_address_air_to_ground):
        self.__address_air_to_ground = new_address_air_to_ground

    def get_address_air_to_ground(self):
        return self.__address_air_to_ground



@try_to_run
def get_config():
    default_config = try_to_run(lambda: open_yaml())
    config = configurations(
        ce_pin = default_config["radio"]["ce_pin"],
        spi_channel = default_config["radio"]["spi_channel"],
        spi_speed = default_config["radio"]["spi_speed"],
        channel = default_config["radio"]["channel"],
        payload_size = default_config["radio"]["payload_size"],
        data_rate = default_config["radio"]["data_rate"],
        pa_level = default_config["radio"]["pa_level"],
        crc_bytes = default_config["radio"]["crc_bytes"],
        address_ground_to_air = default_config["radio"]["address_ground_to_air"],
        address_air_to_ground = default_config["radio"]["address_air_to_ground"])
    return config


