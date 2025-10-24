sudo apt update
sudo apt install -y git python3 python3-pip build-essential
git clone https://github.com/joan2937/pigpio.git
cd pigpio
make
sudo make install
sudo pigpiod
pigs t
python3 -c "import pigpio; print('pigpio:', pigpio.__file__)"