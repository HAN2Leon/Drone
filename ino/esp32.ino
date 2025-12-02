#include <Arduino.h>
#include <RF24.h>

// ===================== 配置区域（原来 YAML 的内容） =====================

// 根据你实际接线改
// 发送端 / 接收端都用同样的 CE/CSN 引脚
static const uint8_t PIN_CE   = 17;
static const uint8_t PIN_CSN  = 5;

// 这两个脚在你的 Python 里既用于输入也用于输出，
// 这里我们约定：发送端作为输入（读开关），接收端作为输出（点灯）。
static const uint8_t PIN_FLAG1 = 17;  // 根据需要改，不要和 CE 冲突
static const uint8_t PIN_FLAG2 = 27;

// RF 通信参数
static const uint8_t  RADIO_CHANNEL      = 76;
static const uint8_t  RADIO_PAYLOAD_SIZE = 32;   // 和 Python struct("<dI??18s") 一致
// 速率、功率、CRC 这里用简单常量映射（你可以按自己原来 YAML 再细调）
static const uint8_t  RADIO_DATARATE     = 2;    // 0:250kbps, 1:1Mbps, 2:2Mbps
static const uint8_t  RADIO_PA_LEVEL     = 3;    // 0..3 -> MIN..MAX
static const uint8_t  RADIO_CRC_BYTES    = 2;    // 0=disable,1=8bit,2=16bit

// 地址（5 字节），原来是 YAML 里的 address_ground_to_air / air_to_ground
// 你可以自己换成真实的：
static const uint8_t ADDRESS_GROUND_TO_AIR[5] = {'N','O','D','E','1'};
static const uint8_t ADDRESS_AIR_TO_GROUND[5] = {'N','O','D','E','2'};

// 发送循环周期（秒）——对应 Python 的 "peroid"
static const float SEND_PERIOD_SEC = 0.1f;  // 0.1s 一次，可改

// 选择角色：true = 作为发送端，false = 作为接收端
static const bool ROLE_IS_TRANSMITTER = false;

// ===================== NRF24 Payload 结构（对齐 Python 的 struct） =====================
// Python: struct.pack("<dI??18s", time_interval, seq, flag1, flag2, text)
// 小端：double(8) + uint32(4) + bool(1) + bool(1) + 18 字节字符串 = 32 字节

#pragma pack(push, 1)
struct RadioPayload {
  double   time_interval;      // 8
  uint32_t seq;                // 4
  bool     flag1;              // 1
  bool     flag2;              // 1
  char     text[18];           // 18
};
#pragma pack(pop)

static_assert(sizeof(RadioPayload) == 32, "RadioPayload must be 32 bytes");

// ===================== 全局 RF24 对象 =====================

RF24 radio(PIN_CE, PIN_CSN);

// ===================== NRF24 初始化（替代 Python init_nRF24） =====================

bool initRadio(bool asTransmitter)
{
  if (!radio.begin()) {
    Serial.println("[ERROR] NRF24 init failed");
    return false;
  }

  radio.setChannel(RADIO_CHANNEL);

  // 数据速率映射
  switch (RADIO_DATARATE) {
    case 0: radio.setDataRate(RF24_250KBPS); break;
    case 1: radio.setDataRate(RF24_1MBPS);   break;
    case 2: radio.setDataRate(RF24_2MBPS);   break;
    default: radio.setDataRate(RF24_1MBPS);  break;
  }

  // 发射功率映射
  switch (RADIO_PA_LEVEL) {
    case 0: radio.setPALevel(RF24_PA_MIN);  break;
    case 1: radio.setPALevel(RF24_PA_LOW);  break;
    case 2: radio.setPALevel(RF24_PA_HIGH); break;
    case 3: radio.setPALevel(RF24_PA_MAX);  break;
    default: radio.setPALevel(RF24_PA_MAX); break;
  }

  // CRC 长度
  if (RADIO_CRC_BYTES == 2) {
    radio.setCRCLength(RF24_CRC_16);
  } else if (RADIO_CRC_BYTES == 1) {
    radio.setCRCLength(RF24_CRC_8);
  } else {
    radio.disableCRC();
  }

  // Payload 长度（你也可以用动态载荷）
  radio.setPayloadSize(RADIO_PAYLOAD_SIZE);
  // radio.enableDynamicPayloads();

  // 自动 ACK
  radio.setAutoAck(true);

  if (asTransmitter) {
    // 发送端：打开写入管道
    radio.openWritingPipe(ADDRESS_GROUND_TO_AIR);
    radio.stopListening();
  } else {
    // 接收端：打开接收管道
    radio.openReadingPipe(1, ADDRESS_GROUND_TO_AIR);
    radio.startListening();
  }

  Serial.println("[INFO] NRF24 initialized");
  return true;
}

// ===================== 接收端逻辑：start_reading 的 C++ 版本 =====================

void loopReceiver()
{
  static bool i1 = true;
  static bool flag2_prev = false;
  static unsigned long last_t_ms = millis();

  // 对应 Python: pi.write(27, False) 初始
  digitalWrite(PIN_FLAG2, LOW);

  if (millis() - last_t_ms > 100) {
    digitalWrite(PIN_FLAG2, LOW);
  }

  while (radio.available()) {
    last_t_ms = millis();
    RadioPayload payload;
    radio.read(&payload, sizeof(payload));

    // 处理文本：去掉末尾 \0
    char textBuf[19] = {0};
    memcpy(textBuf, payload.text, 18);
    textBuf[18] = '\0';

    bool flag1 = payload.flag1;
    bool flag2 = payload.flag2;

    if (i1 && flag1) {
      digitalWrite(PIN_FLAG1, flag1 ? HIGH : LOW);
      i1 = false;
    }

    if (flag2 != flag2_prev) {
      digitalWrite(PIN_FLAG2, flag2 ? HIGH : LOW);
    }
    flag2_prev = flag2;

    Serial.print("Seq: ");
    Serial.print(payload.seq);
    Serial.print(" | Flag1: ");
    Serial.print(flag1);
    Serial.print(" | Flag2: ");
    Serial.print(flag2);
    Serial.print(" | Text: ");
    Serial.println(textBuf);
  }
}

// ===================== 简单的“获取文本”的方式 =====================
// 原来 Python 用 input()，在 MCU 上没终端，这里简单用常量。
// 如果你想用串口输入，可以之后再扩展。

const char* DEFAULT_TEXT = "Hello from ESP32";

// ===================== 发送端逻辑：send_fixed_cycle 的 C++ 版本 =====================

void loopTransmitter()
{
  static bool initialized = false;
  static RadioPayload payload;
  static uint32_t seq = 0;
  static bool flag1 = false;
  static bool flag2 = false;
  static bool flag1_prev = false;
  static bool flag2_prev = false;
  static bool i1 = true;
  static bool i2 = true;
  static unsigned long next_t_ms = 0;

  if (!initialized) {
    // 对应 form_message_payload() 里的初始化
    memset(&payload, 0, sizeof(payload));
    strncpy(payload.text, DEFAULT_TEXT, 18);
    payload.time_interval = 0.0;
    payload.seq = 0;
    payload.flag1 = false;
    payload.flag2 = false;

    seq = 0;
    flag1 = false;
    flag2 = false;
    flag1_prev = false;
    flag2_prev = false;
    i1 = true;
    i2 = true;
    next_t_ms = millis();

    Serial.println("Transmission started.");
    initialized = true;
  }

  unsigned long t0_ms = millis();

  // 读取输入引脚，模拟 Python 的 pi.read(17/27)
  bool flag1_now = digitalRead(PIN_FLAG1);
  if (i1 && !flag1_prev && flag1_now) {
    flag1 = flag1_now;
    i1 = false;
  }
  flag1_prev = flag1_now;

  bool flag2_now = digitalRead(PIN_FLAG2);
  if (i2 && !flag2_prev && flag2_now) {
    flag2 = flag2_now;
    i2 = false;
  }
  if (!i2) {
    flag2 = flag2_now;
  }
  flag2_prev = flag2_now;

  // 更新 payload 的 time_interval / seq / flags
  // time_interval 先占位，等周期结束再算
  payload.seq   = seq;
  payload.flag1 = flag1;
  payload.flag2 = flag2;

  bool ok = radio.write(&payload, sizeof(payload));
  if (!ok) {
    Serial.println("[ERREUR] Perte de liaison — ACK manquant");
  } else {
    char textBuf[19] = {0};
    memcpy(textBuf, payload.text, 18);
    textBuf[18] = '\0';

    Serial.print("Seq: ");
    Serial.print(seq);
    Serial.print(" | Flag1: ");
    Serial.print(flag1);
    Serial.print(" | Flag2: ");
    Serial.print(flag2);
    Serial.print(" | Text: ");
    Serial.println(textBuf);
  }

  seq++;

  // 周期控制：对应 Python 的 next_t/remaining 逻辑
  unsigned long period_ms = (unsigned long)(SEND_PERIOD_SEC * 1000.0f);
  next_t_ms += period_ms;

  unsigned long now = millis();
  if ((long)(next_t_ms - now) > 0) {
    payload.time_interval = (now - t0_ms) / 1000.0;  // 秒
    delay(next_t_ms - now);
  } else {
    payload.time_interval = (now - t0_ms) / 1000.0;
    next_t_ms = now;
  }
}

// ===================== Arduino 标准入口 =====================

void setup()
{
  Serial.begin(115200);
  delay(2000);

  pinMode(PIN_FLAG1, ROLE_IS_TRANSMITTER ? INPUT : OUTPUT);
  pinMode(PIN_FLAG2, ROLE_IS_TRANSMITTER ? INPUT : OUTPUT);

  if (!initRadio(ROLE_IS_TRANSMITTER)) {
    Serial.println("[FATAL] initRadio failed, halt.");
    while (1) { delay(1000); }
  }
}

void loop()
{
  if (ROLE_IS_TRANSMITTER) {
    loopTransmitter();
  } else {
    loopReceiver();
  }
}
