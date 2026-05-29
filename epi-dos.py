#!/usr/bin/env python3

from core.voice_llm import llm
from core.llm_with_contexte import llm as llm_with_contexte

def init():
    print("\n")
    print("Bonjour utilisateur\n")
    print("Que voulez vous faire ?\n")
    print("1 : llm with voice.\n")
    print("2 : llm with context and voice.\n")
    choice = input("donne ton choix : ")

    if (int(choice) == 1):
        llm()
    if (int(choice) == 2):
        llm_with_contexte()
    if (int(choice) != 0):
        return

if __name__ == "__main__":
    init()
