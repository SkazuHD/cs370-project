FROM python:3.11-slim-bullseye AS release

ENV WORKSPACE_ROOT=/llm_engineering/
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    DEBIAN_FRONTEND=noninteractive \
    POETRY_NO_INTERACTION=1

RUN apt-get update -y && apt-get install -y --no-install-recommends \
    wget \
    curl \
    gnupg \
    build-essential \
    gcc \
    python3-dev \
    libglib2.0-dev \
    libnss3-dev \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | \
    gpg --dearmor -o /usr/share/keyrings/google-linux-signing-key.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/google-linux-signing-key.gpg] https://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update -y && apt-get install -y --no-install-recommends google-chrome-stable \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/*

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION" && \
    poetry config installer.max-workers 20 && \
    poetry config virtualenvs.create false

WORKDIR $WORKSPACE_ROOT

COPY pyproject.toml poetry.lock $WORKSPACE_ROOT
RUN poetry install --no-root --no-interaction --no-cache --without dev && \
    poetry self add 'poethepoet[poetry_plugin]' && \
    rm -rf ~/.cache/pypoetry/*

RUN curl -fsSL https://ollama.com/install.sh | sh
RUN ollama --version

RUN bash -c "ollama serve & sleep 5 && ollama pull llama3.1"

# Ensure app.py is copied

EXPOSE 7860

COPY . $WORKSPACE_ROOT


RUN poetry install


#ENTRYPOINT ["bash", "-c", "pwd && ls && poetry run python3 ./app/app.py"]
CMD ["bash", "-c", "ollama serve & poetry run python3 ./app/app.py"]
