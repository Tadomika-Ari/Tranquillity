import os
import shutil
import subprocess
import sys


IMAGE_ENV = "TRANQUILLITY_IMAGE"


def main() -> int:
    image = os.environ.get(IMAGE_ENV)
    if not image:
        print(
            f"{IMAGE_ENV} n'est pas defini. Exemple: "
            "export TRANQUILLITY_IMAGE=USERNAME/tranquillity:latest",
            file=sys.stderr,
        )
        return 2

    if shutil.which("docker") is None:
        print("Docker est requis mais la commande docker est introuvable.", file=sys.stderr)
        return 127

    try:
        subprocess.run(["docker", "info"], check=True)
        subprocess.run(["docker", "pull", image], check=True)
        docker_command = [
            "docker",
            "run",
            "--rm",
            "-it",
            "--name",
            "tranquillity",
        ]
        if os.path.exists("/dev/snd"):
            docker_command.extend(["--device", "/dev/snd:/dev/snd"])
            audio_group = shutil.which("getent")
            if audio_group:
                audio_gid = subprocess.run(
                    [audio_group, "group", "audio"],
                    check=False,
                    capture_output=True,
                    text=True,
                ).stdout.strip().split(":")[-2]
                if audio_gid.isdigit():
                    docker_command.extend(["--group-add", audio_gid])
        docker_command.extend([image, *sys.argv[1:]])
        return subprocess.run(docker_command).returncode
    except subprocess.CalledProcessError as error:
        return error.returncode
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
