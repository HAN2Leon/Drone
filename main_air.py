import radio
from debug import try_to_run


@try_to_run
def main_interaction():
    welcome = "Welcome !\n Would you like to initiate the antenna ? Please answer \"yes\" or \"no\"."
    if input(welcome).strip().lower() in ("true","1","yes","y","vrai","oui") == True:
        nRF24, config= radio.init_nRF24()
        while True :
            send_or_receive = "Should we transmit or receive ? Please answer \"tx\" or \"rx\", type \"q\" for quit."
            if input(send_or_receive).strip().lower() == "tx" :
                nRF24.open_writing_pipe(config["addresses"]["address_air_to_ground"])
                #!!!!!!!!!!!!!!!!!!!!!!!
                while True:
                    times = "Should we transmit only once or by fixed cycle ? Please answer \"onon\" or \"ficy\", type \"q\" for quit."
                    if input(times).strip().lower() == "onon" :
                        radio.send_once(nRF24)
                    elif input(times).strip().lower() == "ficy" :
                        while True:
                            assignment = input("Please assign a value to the period").strip()
                            try:
                                period = float(assignment)
                                radio.send_fixed_cycle(nRF24, period)
                                break 
                            except ValueError:
                                print("[ERROR] Unexpected input. Please try again.")
                    elif input(times).strip().lower() == "q" :
                        break
                    else :
                        print("[ERROR] Unexpected input. Please try again.")    
            elif input(send_or_receive).strip().lower() == "rx" :
                nRF24.open_reading_pipe(1, config["addresses"]["address_ground_to_air"])
                #!!!!!!!!!!!!!!!!!!!!!!!
                radio.start_reading(nRF24)
            elif input(send_or_receive).strip().lower() == "q" :
                print("Goodbye, till next time !")
                break
            else :
                print("[ERROR] Unexpected input. Please try again.")  
    else :
        print("Goodbye, till next time !")

if __name__ == "__main__" :
    main_interaction()