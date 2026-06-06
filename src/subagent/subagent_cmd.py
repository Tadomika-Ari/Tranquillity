import os
import re

FIFO_PATH = "/tmp/kitty_shell_input"

def send_command(cmd: str):
    if not os.path.exists(FIFO_PATH):
        print(f"Sub-Agent: FIFO introuvable: {FIFO_PATH}")
        return
    with open(FIFO_PATH, "w") as fifo:
        fifo.write(cmd + "\n")

def subagent_cmd(cmd: str):
    cmd_s = re.search(r"<cmd>(.*?)</cmd>", cmd)
    if cmd_s:
        send_command(cmd_s.group(1))
    else:
        return 