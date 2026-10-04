from src.ctOS.start.init import demo
from src.ctOS.start.start import start
from src.ctOS.help import help
import sys
import asyncio
from src.subsystem.notification_system import send_discord_message
from dotenv import load_dotenv
from src.tranquillity import init as tranquillity
from src.ctOS.music.music import music_command
from src.ctOS.music.init_token import init
load_dotenv()

def main():
    nb = len(sys.argv)
    
    if nb <= 1:
        help()
        return
    if sys.argv[1] == "--demo":
        demo()
        start()
        return
    if sys.argv[1] == "--music":
        music_command()
        return
    if sys.argv[1] == "--send":
        if sys.argv[2] == None:
            return 84
        asyncio.run(send_discord_message(sys.argv[2]))
        return
    if sys.argv[1] == "--init":
        init()
        return
    if sys.argv[1] == "--start":
        tranquillity()
        return
    if sys.argv[1] == "--help" or "-h":
        help()
    else:
        return 84

if __name__ == "__main__":
    main()