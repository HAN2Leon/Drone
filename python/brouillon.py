"""
Module minimal d'E/S pour nRF24L01.
Fonctions fournies (7) :
  1) init_radio                  — initialisation à partir de paramètres EXTERNES
  2) tx_send_once(radio, payload)— émission d’une trame unique
  3) rx_read_once(radio)         — lecture d’une trame si disponible

Contraintes :
- Aucun accès YAML ici ; tous les paramètres sont fournis par l’appelant.
- Aucune impression/print ; aucune vérification d’état ; aucune boucle/temporisation.
- Le basculement de mode (power_up_tx/rx, power_down) est à la charge de l’appelant.
"""


# Import facultatif des énumérations si disponibles dans votre pilote.
try:
    from nrf24 import RF24_DATA_RATE, RF24_PA, RF24_CRC, RF24_PAYLOAD
except Exception:
    RF24_DATA_RATE = object  # type: ignore
    RF24_PA = object         # type: ignore
    RF24_CRC = object        # type: ignore
    RF24_PAYLOAD = object    # type: ignore


def init_radio(
    pi: pigpio.pi,
    *,
    ce_pin: int,
    spi_channel: int,
    spi_speed: int,
    channel: int,
    data_rate,
    pa_level,
    crc_bytes,
    payload_mode,
    address_bytes: int = 5,
) -> NRF24:
    """
    Initialise le nRF24L01 à partir de paramètres EXTERNES.
    - Ne lit pas de fichier de configuration.
    - N’ouvre aucun pipe TX/RX, ne lance aucune boucle.
    - À la fin, tente un power_down pour laisser l’appelant piloter le mode.

    Paramètres :
      pi            : instance pigpio connectée
      ce_pin        : broche CE (BCM)
      spi_channel   : canal SPI (0/1 ou équivalents)
      spi_speed     : vitesse SPI en Hz
      channel       : canal RF (0..125)
      data_rate     : débit (ex. RF24_DATA_RATE.RATE_1MBPS)
      pa_level      : puissance PA (ex. RF24_PA.MAX)
      crc_bytes     : octets de CRC (0/1/2 ou RF24_CRC.*)
      payload_mode  : RF24_PAYLOAD.DYNAMIC (longueur dynamique) OU 1..32 (fixe)
      address_bytes : largeur d’adresse (3..5)
    Retour :
      Instance NRF24 initialisée.
    """
    taille_payload = (
        0
        if (hasattr(RF24_PAYLOAD, "DYNAMIC") and payload_mode == getattr(RF24_PAYLOAD, "DYNAMIC"))
        else int(payload_mode)
    )

    try:
        radio.power_down()
    except Exception:
        pass  # Silencieux : certains pilotes peuvent ne pas implémenter cette méthode.

    return radio







class Settings:

    _ALLOWED_STR = {
        ("radio", "data_rate"): {"250K", "1M", "2M"},
        ("radio", "pa_level"): {"MIN", "LOW", "HIGH", "MAX"},
        ("io", "role"): {"TX", "RX"},
    }
    _ALLOWED_INT = {
        ("radio", "crc_bytes"): {0, 1, 2},
        ("radio", "address_bytes"): {3, 4, 5},
    }
    _ALLOWED_BOOL = {
        ("ack_policy", "auto_ack"): {True, False},
    }
    # payload_mode : soit "DYNAMIC", soit int 1..32 (testé séparément)

    def __init__(self, yaml_path: Optional[str] = None) -> None:
        # Stockage interne : sections prévues (vides au départ).
        self._params: Dict[str, Any] = {"radio": {}, "io": {}, "ack_policy": {}}
        if yaml_path:
            self.load_defaults(yaml_path)

    # ─────────────────────────────────────────────────────────────────────
    # 1) Charger YAML comme valeurs par défaut (facultatif)
    # ─────────────────────────────────────────────────────────────────────
    def load_defaults(self, yaml_path: str) -> None:
        """
        Charger un fichier YAML et copier ses valeurs dans le stockage interne.
        - Mappage des clés YAML → schéma interne (sans conversion de format).
        - Silencieux si le fichier est absent/invalide (aucune exception propagée).
        """
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
        except Exception:
            return

        mapped = self._map_yaml_keys(raw)
        self._overwrite(self._params, mapped)

    # ─────────────────────────────────────────────────────────────────────
    # 2) Écrasement direct des valeurs courantes
    # ─────────────────────────────────────────────────────────────────────
    def set(self, params: Dict[str, Any], *, check_enums: bool = False) -> Dict[str, Any]:
        """
        Écraser directement les paramètres courants avec `params`.
        - Aucune normalisation / conversion.
        - Option : contrôle d’appartenance aux ensembles autorisés (si check_enums=True).
        - Retourne une COPIE des paramètres après écrasement.
        """
        if params:
            self._overwrite(self._params, params)
        if check_enums:
            self._check_enums(self._params)
        return copy.deepcopy(self._params)

    # ─────────────────────────────────────────────────────────────────────
    # 3) Lecture simple
    # ─────────────────────────────────────────────────────────────────────
    def get(self) -> Dict[str, Any]:
        """Retourner une COPIE des paramètres courants (aucun effet de bord)."""
        return copy.deepcopy(self._params)

    # ─────────────────────────────────────────────────────────────────────
    # Internes : mapping YAML, écrasement, contrôle léger
    # ─────────────────────────────────────────────────────────────────────
    @staticmethod
    def _map_yaml_keys(yaml_raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapper les clés usuelles du YAML fourni vers les clés internes.
        - Pas de normalisation de valeurs : on recopie tel quel.
        - Clés attendues dans le YAML :
            radio.CE_PIN        → radio.ce_pin
            radio.SPI_CHANNEL   → radio.spi_channel
            radio.SPI_SPEED     → radio.spi_speed
            radio.CHANNEL       → radio.channel
            radio.payload_size  → radio.payload_mode
            radio.data_rate     → radio.data_rate
            radio.pa_level      → radio.pa_level
            radio.crc_bytes     → radio.crc_bytes
            radio.address_bytes → radio.address_bytes
            addresses.ADDR      → radio.address
        """
        out = {"radio": {}, "io": {}, "ack_policy": {}}
        r = (yaml_raw or {}).get("radio", {}) or {}
        a = (yaml_raw or {}).get("addresses", {}) or {}

        # Champs directs (copie brute)
        if "CE_PIN" in r:
            out["radio"]["ce_pin"] = r["CE_PIN"]
        if "SPI_CHANNEL" in r:
            out["radio"]["spi_channel"] = r["SPI_CHANNEL"]
        if "SPI_SPEED" in r:
            out["radio"]["spi_speed"] = r["SPI_SPEED"]
        if "CHANNEL" in r:
            out["radio"]["channel"] = r["CHANNEL"]

        # Optionnels
        if "payload_size" in r:
            out["radio"]["payload_mode"] = r["payload_size"]
        if "data_rate" in r:
            out["radio"]["data_rate"] = r["data_rate"]
        if "pa_level" in r:
            out["radio"]["pa_level"] = r["pa_level"]
        if "crc_bytes" in r:
            out["radio"]["crc_bytes"] = r["crc_bytes"]
        if "address_bytes" in r:
            out["radio"]["address_bytes"] = r["address_bytes"]

        # Adresse
        if "ADDR" in a:
            out["radio"]["address"] = a["ADDR"]

        return out

    @staticmethod
    def _overwrite(base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """
        Écraser champ par champ dans les sections prévues ('radio', 'io', 'ack_policy').
        - Si une sous-clé est fournie, elle remplace la valeur existante.
        - Pas de vérification, pas d’effets collatéraux.
        """
        if not override:
            return
        for section in ("radio", "io", "ack_policy"):
            src = override.get(section)
            if isinstance(src, dict):
                dst = base.setdefault(section, {})
                for k, v in src.items():
                    dst[k] = v

    def _check_enums(self, params: Dict[str, Any]) -> None:
        """
        Contrôle minimal d’appartenance aux ENSEMBLES CANONIQUES.
        - data_rate : "250K" | "1M" | "2M"
        - pa_level  : "MIN" | "LOW" | "HIGH" | "MAX"
        - role      : "TX" | "RX"
        - crc_bytes : 0 | 1 | 2
        - address_bytes : 3 | 4 | 5
        - auto_ack  : True | False
        - payload_mode : "DYNAMIC" OU entier 1..32
        - (channel/ce_pin/spi_* : pas de contrôle ici, le frontal doit garantir)
        Lève ValueError si une valeur fournie n’appartient pas à l’ensemble autorisé.
        """
        # Chaînes
        for (sec, key), allowed in self._ALLOWED_STR.items():
            v = params.get(sec, {}).get(key, None)
            if v is None:
                continue
            if not isinstance(v, str) or v not in allowed:
                raise ValueError(f"valeur non autorisée (chaîne) : {sec}.{key} = {v}")

        # Entiers (ensembles bornés)
        for (sec, key), allowed in self._ALLOWED_INT.items():
            v = params.get(sec, {}).get(key, None)
            if v is None:
                continue
            if not isinstance(v, int) or v not in allowed:
                raise ValueError(f"valeur non autorisée (entier) : {sec}.{key} = {v}")

        # Booléens
        for (sec, key), allowed in self._ALLOWED_BOOL.items():
            v = params.get(sec, {}).get(key, None)
            if v is None:
                continue
            if v not in allowed:  # accepte True/False exact
                raise ValueError(f"valeur non autorisée (bool) : {sec}.{key} = {v}")

        # payload_mode : "DYNAMIC" ou 1..32
        pm = params.get("radio", {}).get("payload_mode", None)
        if pm is not None:
            if isinstance(pm, str):
                if pm != "DYNAMIC":
                    raise ValueError(f"payload_mode invalide : {pm}")
            elif isinstance(pm, int):
                if not (1 <= pm <= 32):
                    raise ValueError(f"payload_mode hors plage (1..32) : {pm}")
            else:
                raise ValueError(f"payload_mode type invalide : {type(pm).__name__}")
