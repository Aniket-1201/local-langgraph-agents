# Use a lightweight Python base image
FROM python:3.10-slim

# Install system dependencies (curl is needed to download Ollama)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Ollama natively in the Linux container
RUN curl -fsSL https://ollama.com/install.sh | sh

# Hugging Face Spaces Security Requirement: Create a non-root user
RUN useradd -m -u 1000 user

# Set up the environment variables for the new user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set the working directory
WORKDIR $HOME/app

# Change ownership of the working directory to our non-root user
RUN chown -R user:user $HOME/app

# Switch to the non-root user
USER user

# Copy requirements and install Python dependencies
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files (including the .gguf, Modelfile, and python scripts)
COPY --chown=user:user . .

# Make the bash script executable
RUN chmod +x start.sh

# Expose port 7860
EXPOSE 7860

# Tell Docker to run the bash script when the container turns on
CMD ["./start.sh"]