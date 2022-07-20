# coding: utf-8

import contextlib
from collections import defaultdict
import time

from PyQt5.QtCore import Qt
from pynput import keyboard
import pyperclip as pc

from pikayboard.liste_francais import liste_francais

import sys
from PyQt5.QtWidgets import QWidget, QApplication, QListWidget, QGridLayout, QPushButton, QVBoxLayout, QDesktopWidget

import threading


class Kyb:
    def __init__(self):
        self.kb = keyboard.Controller()
        self.current = defaultdict(bool)

        self.key_pressed = ""
        self.key_pressed_list = ""
        self.key_pressed_list_start_letter = ""
        self.key_pressed_list_save = ""
        self.len_key_pressed_list = 0
        self.len_key_pressed_list_save = ""

        self.number_of_tab = 0

        self.erase_tab = False
        self.count_backspace = 0
        self.auto_complete_on = False

        self.i = 0

        self.json_word_liste = liste_francais
        self.json_word_liste.update(
            {
                "start_letter": []
            }
        )

    def listener_handler(self, kyb):
        with keyboard.Listener(
                on_press=kyb.loop,
                on_release=kyb.on_release) as self.listener:
            self.listener.join()

    def append_key_pressed_list(self):
        with contextlib.suppress(TypeError):
            self.key_pressed_list += self.key_pressed
            self.len_key_pressed_list = len(self.key_pressed_list)
            self.key_pressed_list_start_letter = self.key_pressed_list[:1]

    def save_key(self, key):
        self.current[key] = True
        try:
            self.key_pressed = key.char
            self.append_key_pressed_list()
        except AttributeError:
            self.key_pressed = key

    def save_key_pressed_list(self):
        self.key_pressed_list = self.key_pressed_list

    def clear_key_pressed_list(self):
        self.key_pressed = ""
        self.key_pressed_list = ""
        self.key_pressed_list_start_letter = ""
        self.key_pressed_list = ""
        self.len_key_pressed_list = 0

        self.number_of_tab = 0

    def activate_erase_tab(self):
        self.erase_tab = not self.erase_tab
        if kyb.erase_tab:
            graphic_app.erase_tab_button.setText("Déactivé la suppression de la tabulation supplémentaire")
        else:
            graphic_app.erase_tab_button.setText("Activé la suppression de la tabulation supplémentaire")

    def activate_auto_complete(self):
        self.auto_complete_on = not self.auto_complete_on
        if kyb.auto_complete_on:
            graphic_app.auto_complete_on_button.setText("Déactivé la completion automatique")
        else:
            graphic_app.auto_complete_on_button.setText("Activé la completion automatique")
            self.clear_key_pressed_list()
            self.key_pressed_list = ""

    def update_word_list(self):
        if self.number_of_tab == 0:
            self.key_pressed_list_save = self.key_pressed_list
            self.len_key_pressed_list_save = self.len_key_pressed_list
        if self.len_key_pressed_list_save == 1:
            self.json_word_liste["start_letter"] = []
            for word in self.json_word_liste[self.key_pressed_list_start_letter]:
                self.json_word_liste["start_letter"].append(word)
        elif self.len_key_pressed_list_save > 1:
            self.json_word_liste["start_letter"] = []
            for word in self.json_word_liste[self.key_pressed_list_start_letter]:
                if word.startswith(self.key_pressed_list_save) and word != self.key_pressed_list_save:
                    self.json_word_liste["start_letter"].append(word)

        graphic_app.update_list_of_word()

    def delete_last_word(self):
        for _ in range(self.len_key_pressed_list):
            self.kb.press(keyboard.Key.left)
            self.kb.release(keyboard.Key.left)

        for _ in range(self.len_key_pressed_list):
            self.kb.press(keyboard.Key.delete)
            self.kb.release(keyboard.Key.delete)

        self.kb.release(keyboard.Key.delete)
        self.key_pressed_list = ""
        self.len_key_pressed_list = 0

    def auto_complete_text(self, word=False):
        self.update_word_list()
        if self.json_word_liste["start_letter"] and self.auto_complete_on:
            self.delete_last_word()

            if self.erase_tab:
                self.kb.press(keyboard.Key.left)
                self.kb.release(keyboard.Key.left)
                self.kb.press(keyboard.Key.delete)
                self.kb.release(keyboard.Key.delete)

            if self.erase_tab:
                time.sleep(0.1)

            if self.number_of_tab > (len(self.json_word_liste["start_letter"]) - 1) \
                    or len(self.json_word_liste["start_letter"]) == 1:
                self.number_of_tab = 0

            if not word:
                word = self.json_word_liste["start_letter"][self.number_of_tab]

            for key in word:
                self.kb.press(key)
                self.kb.release(key)
            self.number_of_tab += 1

    def get_current_key(self):
        return [k for k, v in self.current.items() if v]

    def check_key(self, key):
        separate_key = [
            "'", "(", ")", "\"", "[", "]", "{", "}", '`', "@", "\\", "/", "|", ".",
            ",", ";", "?", ":", "!", "§", "%", "<", ">", keyboard.Key.space, keyboard.Key.enter
        ]

        if self.key_pressed in separate_key:
            self.clear_key_pressed_list()
            self.key_pressed_list = ""

        elif key == keyboard.Key.backspace:
            self.kb.press("a")
            self.delete_last_word()
            self.clear_key_pressed_list()

        elif key == keyboard.Key.tab:
            self.auto_complete_text()

    def loop(self, key):
        self.save_key(key)

        if key == keyboard.Key.end:
            self.clear_key_pressed_list()
        elif self.key_pressed_list != "":
            self.check_key(key)

    def on_release(self, key):
        self.current[key] = False
        self.key_pressed = ""


class GraphicApp(QWidget):
    def __init__(self):
        super(GraphicApp, self).__init__()

        self.auto_complete_on_button = None
        self.erase_cache_button = None
        self.erase_tab_button = None
        self.list_of_word = None
        self.json_word_list_save = None

        self.center()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.init_ui()

    def update_list_of_word(self):
        if self.json_word_list_save != kyb.json_word_liste["start_letter"]:
            self.json_word_list_save = kyb.json_word_liste["start_letter"]
            for num, word in enumerate(kyb.json_word_liste["start_letter"]):
                self.list_of_word.insertItem(num, word)

    def word_clicked(self):
        word = self.list_of_word.currentItem().text()
        pc.copy(word)
        kyb.clear_key_pressed_list()

    def closeEvent(self, event):
        kyb.listener.stop()
        kyb.kb.press(keyboard.Key.end)
        kyb.kb.release(keyboard.Key.end)
        sys.exit()

    def init_ui(self):
        self.setWindowTitle("Pikayboard")

        layout_grid = QGridLayout()
        layout_root = QVBoxLayout()
        self.setLayout(layout_root)

        self.list_of_word = QListWidget()
        self.list_of_word.clicked.connect(self.word_clicked)
        layout_root.addWidget(self.list_of_word)

        self.auto_complete_on_button = QPushButton()
        self.auto_complete_on_button.clicked.connect(kyb.activate_auto_complete)
        if kyb.auto_complete_on:
            self.auto_complete_on_button.setText("Déactivé la completion automatique")
        else:
            self.auto_complete_on_button.setText("Activé la completion automatique")
        layout_grid.addWidget(self.auto_complete_on_button, 0, 0)

        self.erase_cache_button = QPushButton()
        self.erase_cache_button.clicked.connect(kyb.clear_key_pressed_list)
        self.erase_cache_button.setText("Supprimer le cache")
        layout_grid.addWidget(self.erase_cache_button, 0, 1)

        layout_root.addLayout(layout_grid)

        self.erase_tab_button = QPushButton()
        self.erase_tab_button.clicked.connect(kyb.activate_erase_tab)
        if kyb.erase_tab:
            self.erase_tab_button.setText("Déactivé la suppression de la tabulation supplémentaire")
        else:
            self.erase_tab_button.setText("Activé la suppression de la tabulation supplémentaire")
        layout_root.addWidget(self.erase_tab_button)

        self.update_list_of_word()
        self.show()

    def center(self):
        width = 450
        height = 270

        self.setGeometry(0, 0, width, height)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())


kyb = Kyb()
app = QApplication(sys.argv)
graphic_app = GraphicApp()


def keyboard_thread():
    kyb.listener_handler(kyb)


def start():
    threading.Thread(target=keyboard_thread).start()

    sys.exit(app.exec_())

