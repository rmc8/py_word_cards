import os
from random import shuffle as shf
from glob import glob
from typing import Optional

import pandas as pd
import PySimpleGUI as sg


def setup_the_card(card_path_list: list) -> Optional[dict]:
    cards_dict = {os.path.basename(path): path for path in card_path_list}
    menu_values = list(cards_dict.keys())
    layout = [[sg.Text("Please choose a card to use for learning!")],
              [sg.Combo(menu_values, size=(48, 2))],
              [sg.Checkbox("Shuffle the words")],
              [sg.Checkbox("Learn only the flagged words")],
              [sg.Text("")],
              [sg.Button("OK"), sg.Button("Exit")]]
    window = sg.Window("Setup the card", layout)
    
    # Event Loop to process "events" and get the "values" of the inputs
    ret = None
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "Exit":
            break
        elif event == "OK":
            if not values[0]:
                sg.popup("Please select a card.")
            path = cards_dict.get(values[0])
            ret = {"card_path": path, "shuffle": values[1], "flag_only": values[2]}
            break
    window.close()
    return ret


def check_card_exits(deck) -> bool:
    if not deck:
        sg.popup("The card does not exist.\nPlease select a different card.")
        return False
    return True


class WordCards:
    def __init__(self, card_path: str, shuffle: bool, flag_only: bool) -> None:
        self.card_path = card_path
        self.shuffle = shuffle
        self.flag_only = flag_only
        self.df = pd.read_csv(card_path)
    
    def get_the_deck(self) -> list:
        deck = self.df
        if self.flag_only:
            deck = deck[deck["flag"] == self.flag_only]
        deck_list = deck.values.tolist()
        if self.shuffle:
            shf(deck_list)
        return deck_list
    
    def update(self, update_list: list) -> None:
        print(self.df.columns)
        for foreign, native, flag in update_list:
            self.df.loc[(self.df["foreign_lang"] == foreign) &
                        (self.df["native_lang"] == native),
                        "flag"] = flag
        self.df.to_csv(self.card_path, index=False)


class MemorizationApp:
    def __init__(self, deck: list, file_name: str):
        self.name = file_name
        self.deck = deck
        self.archive_list = []
        layout = [[sg.Text("", key="foreign_lng", font=("Arial 20"), size=(24, 1))],
                  [sg.Text("", key="native_lng", font=("Consolas 16"), size=(12, 2))],
                  [sg.Checkbox("Shuffle the words", key="flag")],
                  [
                      sg.Button("Display the meaning", size=(24, 2), key="display"),
                      sg.Button("Next", size=(24, 2))
                  ], ]
        self.window = sg.Window(self.name, layout, finalize=True)
    
    def show_word(self, foreign, native, flag):
        self.window["foreign_lng"].update(foreign)
        self.window["native_lng"].update("")
        self.window["flag"].update(flag)
        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                return True, None
            elif event == "display":
                self.window["native_lng"].update(native)
            elif event == "Next":
                break
        return False, values["flag"]
    
    def learning(self):
        for foreign_lng, native_lng, flag in self.deck:
            is_exit, update_flg = self.show_word(foreign_lng, native_lng, flag)
            if is_exit:
                break
            rec = (foreign_lng, native_lng, update_flg)
            self.archive_list.append(rec)
        self.window.close()
    
    def get_new_data(self):
        return self.archive_list


def main():
    sg.theme("black")
    while True:
        cards: list = glob("./cards/*.csv")
        card_setting = setup_the_card(cards)
        if card_setting is None:
            exit()
        wc = WordCards(**card_setting)
        deck: list = wc.get_the_deck()
        card_exist: bool = check_card_exits(deck)
        if not card_exist:
            continue
        name = os.path.basename(card_setting["card_path"])
        ma = MemorizationApp(deck, name)
        ma.learning()
        new_deck = ma.get_new_data()
        wc.update(new_deck)
        sg.popup(f"You have completed learning the deck ({name})!")


if __name__ == "__main__":
    main()
