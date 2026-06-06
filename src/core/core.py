import os
import threading as Thread
import subprocess
import time
import stat
from core.voice_llm import llm
from core.llm_with_contexte import llm as llm_with_context
from core.waiting_message import waiting_message
import core.state as state

FIFO_PATH = "/tmp/kitty_shell_input"

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

def open_kitty_shell():
    if os.path.exists(FIFO_PATH):
        if not stat.S_ISFIFO(os.stat(FIFO_PATH).st_mode):
            os.remove(FIFO_PATH)
            os.mkfifo(FIFO_PATH)
    else:
        os.mkfifo(FIFO_PATH)
    subprocess.Popen(["kitty", "-e", "bash", "-c", f"tail -f {FIFO_PATH} | bash"])

def send_command(cmd: str):
    with open(FIFO_PATH, "w") as fifo:
        fifo.write(cmd + "\n")

def init_shell():
    open_kitty_shell()
    send_command("echo 'initialisation terminé.'")
    
def core():

    t_minuteur = Thread.Thread(target=minuteur, daemon=True)
    t_minuteur.start()

    t_talk = Thread.Thread(target=llm_with_context, daemon=True)
    t_talk.start()

    init_shell()
    while state.is_alive:
        if state.is_alive == 0:
            os.remove(FIFO_PATH)
            break

            