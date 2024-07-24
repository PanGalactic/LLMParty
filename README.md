# LLMParty: Unified JSON API for Language Models

LLMParty is a powerful and flexible Python library that provides a unified interface for interacting with various Language Model (LLM) providers. It allows users to send prompts to different LLMs and receive responses in a standardized JSON format, simplifying the process of working with multiple LLM APIs.

## Features

- Unified API for multiple LLM providers (OpenAI, Anthropic, Ollama, Groq)
- JSON-based input and output for easy integration
- Configurable via YAML for easy customization
- Command-line interface for quick testing and scripting
- Support for piping input for longer prompts or script integration
- Python module for seamless integration into your projects

## Installation

You can install LLMParty using pip:

```bash
pip install llmparty
```

## Configuration

After installation, run the setup command to create a default configuration file:

```bash
llmp-setup
```

This will create a `.llmparty` directory in your home folder with a `config.yaml` file. Edit this file to add your API keys and customize provider settings.

## Usage

### Command Line Interface

LLMParty provides two command-line interfaces: `llmp` and `llmparty`. They can be used interchangeably.

Basic usage:

```bash
llmp -p <provider> -m <model> "<JSON-optimized prompt>"
```

or

```bash
llmparty -p <provider> -m <model> "<JSON-optimized prompt>"
```

Options:
- `-p`, `--provider`: LLM provider (required)
- `-m`, `--model`: Model name (required)
- `-u`, `--show-usage`: Show token usage statistics
- `-v`, `--verbose`: Show additional information from the API response
- `--config`: Path to a custom YAML configuration file

Example:

```bash
llmp -p openai -m gpt-3.5-turbo "Generate a JSON object with a random book title and author."
```

### Piping Input

You can pipe input into LLMParty, which is useful for processing longer prompts or integrating LLMParty into shell scripts:

```bash
echo "Generate a JSON object with three random book titles and their authors." | llmp -p openai -m gpt-3.5-turbo
```

For more complex JSON-optimized prompts:

```bash
cat << EOF | llmp -p openai -m gpt-3.5-turbo
Generate a JSON object representing a recipe for a classic French dish. 
Include fields for name, ingredients (as an array), and steps (as an array). 
Example format: 
{
  "name": "Dish Name",
  "ingredients": ["item1", "item2"],
  "steps": ["step1", "step2"]
}
EOF
```

You can also use files:

```bash
cat long_prompt.txt | llmp -p openai -m gpt-3.5-turbo
```

### Python Module

You can use LLMParty as a Python module in your projects:

```python
from llmparty import LLMParty
import json

party = LLMParty()

request = {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "prompt": "Generate a JSON object with a random book title and author."
}

result = party.produce(request)

print(json.dumps(result['content'], indent=2))
```

## Supported Providers

- OpenAI (GPT models)
- Anthropic (Claude models)
- Ollama (various open-source models)
- Groq

More providers can be added by modifying the `config.yaml` file.

## Optimizing Prompts for JSON Output

To get the best results from LLMParty, it's recommended to explicitly request JSON output in your prompts and provide an example of the desired format. This helps the language models structure their responses consistently.

Example of an optimized prompt:

```
Generate a JSON object describing a random book. Include fields for title, author, publication year, and a brief synopsis. Format the response as valid JSON. Example format:
{
  "title": "Book Title",
  "author": "Author Name",
  "year": 2023,
  "synopsis": "A brief description of the book's plot or contents."
}
```

## Environment Variables

LLMParty uses environment variables for API keys. Make sure to set these before using the corresponding providers:

- OpenAI: `OPENAI_API_KEY`
- Anthropic: `ANTHROPIC_API_KEY`
- Groq: `GROQ_API_KEY`

Ollama typically runs locally and doesn't require an API key.

## Contributing

Contributions to LLMParty are welcome! Here are some ways you can contribute:

1. Report bugs or suggest features by opening issues.
2. Submit pull requests to fix bugs or add new features.
3. Improve documentation or add examples.
4. Add support for new LLM providers.

Please ensure that your code adheres to the existing style and includes appropriate tests and documentation.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all the LLM providers for their amazing models and APIs.
- Inspired by the need for a unified interface to work with multiple LLM providers.

For more detailed information on usage and configuration, please refer to the documentation in the `docs/` directory.
