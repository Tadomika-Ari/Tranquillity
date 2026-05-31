import os
import threading as Thread
import time
from core.voice_llm import llm
from core.llm_with_contexte import llm as llm_with_context
from core.waiting_message import waiting_message
import core.state as state


def minuteur():
    time_nb = 0
    while state.is_alive:
        if not state.time_statue:
            time_nb = 0
            state.time_statue = True
        time.sleep(1)
        time_nb = time_nb + 1    
        if time_nb > state.time_max:
            waiting_message()
            time_nb = 0
        
def core():

    t_minuteur = Thread.Thread(target=minuteur, daemon=True)
    t_minuteur.start()

    t_talk = Thread.Thread(target=llm_with_context, daemon=True)
    t_talk.start()
    while state.is_alive:
        if state.is_alive == 0:
            break

            