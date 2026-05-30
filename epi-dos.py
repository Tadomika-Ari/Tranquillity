#!/usr/bin/env python3

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from core.voice_llm import llm
from core.llm_with_contexte import llm as llm_with_contexte
from core.core import core
from core.waiting_message import waiting_message

def init():
    print("\n")
    print("Bonjour utilisateur\n")
    print("Que voulez vous faire ?\n")
    print("1 : llm with voice.\n")
    print("2 : llm with context and voice.\n")
    print("3 : with threading\n")
    print("4 : waiting message\n")
    choice = input("donne ton choix : ")

    if (int(choice) == 1):
        llm()
    if (int(choice) == 2):
        llm_with_contexte()
    if (int(choice) == 3):
        core()
    if (int(choice) == 4):
        waiting_message()
    if (int(choice) != 0):
        return

if __name__ == "__main__":
    init()
