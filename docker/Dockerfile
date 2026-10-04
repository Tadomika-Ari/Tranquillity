FROM ubuntu:24.04
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv curl git \
    libportaudio2 libgl1 libglib2.0-0t64 \
    && rm -rf /var/lib/apt/lists/*

COPY . /opt/tranquillity
RUN python3 -m venv /opt/venv \
  && /opt/venv/bin/pip install --no-cache-dir -e '/opt/tranquillity[app]'
ENV PATH="/opt/venv/bin:$PATH"

RUN existing_user="$(getent passwd 1000 | cut -d: -f1)" && \
    if [ -n "$existing_user" ]; then \
      usermod --login assistant --home /home/assistant --move-home "$existing_user"; \
    else \
      useradd -m -u 1000 -s /bin/bash assistant; \
    fi

RUN rm -f /bin/rm /usr/bin/rm /sbin/rm /usr/sbin/rm
RUN echo '#!/bin/bash\necho "Erreur : La commande rm a ete desactivee pour la securite de votre systeme."' > /bin/rm \
    && chmod +x /bin/rm

WORKDIR /opt/tranquillity
USER assistant
ENTRYPOINT ["/opt/venv/bin/python", "/opt/tranquillity/ctOS.py"]