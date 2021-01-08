import os
from typing import Optional
from glob import glob

import PySimpleGUI as sg


def setup_the_card(card_path_list: list) -> Optional[dict]:
    cards_dict = {os.path.basename(path): path for path in card_path_list}
    menu_values = list(cards_dict.keys())
    sg.theme("black")
    layout = [[sg.Text("Please choose a card to use for learning!")],
              [sg.Combo(menu_values, size=(48, 2))],
              [sg.Checkbox("Shuffle the words")],
              [sg.Checkbox("Learn only the flagged words")],
              [sg.Text("")],
              [sg.Button("OK"), sg.Button('Exit')]]
    
    # Create the Window
    window = sg.Window('Window Title', layout)
    
    # Event Loop to process "events" and get the "values" of the inputs
    ret = None
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "Exit":
            break
        elif event == "OK":
            if not values[0]:
                sg.popup("Please select a card.")
            ret = {"card_path": values[0], "shuffle": values[1], "flag_only": values[2]}
            break
    window.close()
    return ret


def main():
    cards: list = glob("./cards/*.csv")
    ret = setup_the_card(cards)
    if ret is None:
        exit()
    print(ret)


if __name__ == "__main__":
    main()
