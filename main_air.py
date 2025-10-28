import radio
from debug import try_to_run


@try_to_run
def main_interaction():
    welcome = "Welcome !\nWould you like to initiate the antenna ? Please answer \"yes\" or \"no\".\n"
    if input(welcome).strip().lower() in ("true","1","yes","y","vrai","oui"):
        nRF24, config = radio.init_nRF24()
        while True :
            send_or_receive = "Should we transmit or receive ? Please answer \"tx\" or \"rx\", type \"q\" for quit.\n"
            answer = input(send_or_receive).strip().lower()
            if answer == "tx" :
                nRF24.open_writing_pipe(config.get_address_air_to_ground())
                #!!!!!!!!!!!!!!!!!!!!!!!
                while True:
                    times = "Should we transmit only once or by fixed cycle ? Please answer \"onon\" or \"ficy\", type \"q\" for quit.\n"
                    mode = input(times).strip().lower()
                    if mode == "onon" :
                        radio.send_once(nRF24, config)
                    elif mode == "ficy" :
                        while True:
                            assignment = input("Please assign a value to the period.\n").strip()
                            try:
                                period = float(assignment)
                                radio.send_fixed_cycle(nRF24, period, config)
                                break 
                            except ValueError:
                                print("[ERROR] Unexpected input. Please try again.")
                    elif mode == "q" :
                        break
                    else :
                        print("[ERROR] Unexpected input. Please try again.")    
            elif answer == "rx" :
                nRF24.open_reading_pipe(0, config.get_address_ground_to_air())
                #!!!!!!!!!!!!!!!!!!!!!!!
                radio.start_reading(nRF24)
            elif answer == "q" :
                print("Goodbye, till next time !")
                break
            else :
                print("[ERROR] Unexpected input. Please try again.")  
    else :
        print("Goodbye, till next time !")

if __name__ == "__main__" :
    main_interaction()