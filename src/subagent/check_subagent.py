from subagent.subagent_cmd import subagent_cmd

def check_subagent(response: str):
    if "<cmd>" in response:
        subagent_cmd(response)
    return