Pour installer pigpio sur RPI4:

        sudo apt update
        sudo apt install -y git python3 python3-pip build-essential
        git clone https://github.com/joan2937/pigpio.git
        cd pigpio
        make
        sudo make install
        sudo pigpiod
        pigs t
        python3 -c "import pigpio; print('pigpio:', pigpio.__file__)"


2 services pour demarrage automatique :

1er:

        sudo nano /etc/systemd/system/pigpiod.service

        [Unit]
        Description=Pigpio daemon
        After=network.target

        [Service]
        Type=forking
        ExecStart=/usr/local/bin/pigpiod -l
        ExecStop=/bin/kill -TERM $MAINPID

        [Install]
        WantedBy=multi-user.target

        sudo systemctl daemon-reload
        sudo systemctl enable --now pigpiod

2ème:

        sudo nano /etc/systemd/system/mypro.service

            [Unit]
            Description=My pigpio python program
            After=pigpiod.service
            Requires=pigpiod.service

            [Service]
            Type=simple
            User=bebl
            WorkingDirectory=/home/bebl/Desktop/Drone/python
            ExecStart=/usr/bin/python3 /home/bebl/Desktop/Drone/python/Sol.py
            Restart=always

            [Install]
            WantedBy=multi-user.target

        sudo systemctl daemon-reload
        sudo systemctl enable --now mypro


Pour afficher des journal:

        journalctl -u mypro -f
