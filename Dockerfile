FROM python:3.10-slim

RUN apt-get update && apt-get install -y curl zstd && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://ollama.com/install.sh | sh

RUN useradd -m -u 1000 user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

RUN chown -R user:user $HOME/app

USER user

COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ ADD THIS LINE - installs the hf CLI tool
RUN pip install --no-cache-dir huggingface-hub

COPY --chown=user:user . .

RUN chmod +x start.sh

EXPOSE 7860

CMD ["./start.sh"]