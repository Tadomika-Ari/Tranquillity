# Tranquillity

What is Tranquillity?

Tranquillity is a project that aims to recreate a personal assistant with GLaDOS AI voice, capable of assisting with any task on a PC.

Inspired by the famous AI from the video game Portal 2, as well as projects already created throughout the Internet.

<img src="https://github.com/user-attachments/assets/1f69f6fd-e8fd-4431-956d-32d97b91bb56" 
        alt="Picture" 
        width="800" 
        height="600" 
        style="display: block; margin: 10" />

***

Features:

* **Personal AI Assistant** with GLaDOS voice synthesis (TTS).
* **Voice Recognition** - French language support with rapid command parsing.
* **Music Control** - Spotify integration (pause, resume, device management).
* **Lighting Control** - Smart light management.
* **Discord Integration** - Send messages to Discord directly from commands.
* **ctOS CLI** - Custom command-line interface created specifically for Tranquillity.
* **Voice-to-Voice LLM** - Direct voice conversation with AI processing.

***

Planned Features:

* Enhanced gesture recognition and commands.
* Extended camera vision capabilities.
* Additional smart home integrations.
* More language support.
* And much more.

***

Development / Usage:

For Linux or Windows:

```bash
./env/bin/python -m pip install -r requirement.txt
```

For NixOS:

Requires devenv

```bash
devenv init
```

then

```bash
devenv start
```

Usage:

```bash
python ctOS.py --init
python ctOS.py --start
```

Docker:

```bash
docker build -f docker/Dockerfile -t tranquillity:local .
TRANQUILLITY_IMAGE=tranquillity:local python docker_launcher.py --help

```

The `tranquillity` command from `pyproject.toml` runs `docker_launcher.py` on the host. The Docker image itself runs `ctOS.py` and forwards the arguments supplied to the launcher.

***

Inspiration:

This project wouldn't exist without inspiration and help.
The project is primarily educational, and here are the repositories that helped me:

* https://github.com/dnhkng/GLaDOS

***

I welcome any help!


