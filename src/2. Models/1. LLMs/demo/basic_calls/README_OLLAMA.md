# Ollama - Local SLM Inference

## Prerequisites
- macOS (Apple Silicon recommended), Linux, or Windows
- At least 8 GB RAM (16 GB recommended for 4B+ models)

## Step 1: Install Ollama

1. Go to [https://ollama.com/download](https://ollama.com/download)
2. Download and install the version for your OS
3. Verify the installation:

```bash
ollama --version
```

On macOS, Ollama runs as a background service automatically after installation.

## Step 2: Pull a Model

Pull the `gemma3:4b` model (~3.3 GB download):

```bash
ollama pull gemma3:4b
```

Verify the model is available:

```bash
ollama list
```

You should see `gemma3:4b` in the output.

## Step 3: Run the Script

```bash
uv run "src/2. Models/1. LLMs/demo/5.Ollama_basic_call.py"
```

No API key or `.env` configuration is needed — the script connects to the local Ollama server at `http://localhost:11434`.

## Troubleshooting

- **Connection refused**: Make sure the Ollama service is running (`ollama serve` to start it manually)
- **Model not found**: Run `ollama pull gemma3:4b` to download the model
- **Slow responses**: First inference after pulling a model is slower as it loads into memory; subsequent calls are faster
