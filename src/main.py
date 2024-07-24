# main.py

# Import necessary standard libraries
import os  # For operating system dependent functionality
import json  # For JSON encoding and decoding
import subprocess  # For running shell commands
import argparse  # For parsing command-line arguments
import yaml  # For reading YAML configuration files
import sys  # For system-specific parameters and functions
from pathlib import Path  # For object-oriented filesystem paths
from typing import Dict, Any  # For type hinting

class LLMParty:
    def __init__(self, config_path: str = None):
        """
        Initialize the LLMParty class.
        
        Args:
            config_path (str, optional): Path to the configuration file. Defaults to None.
        """
        # Load the configuration when the class is instantiated
        self.config = self.load_config(config_path)

    def load_config(self, config_path: str = None) -> Dict[str, Any]:
        """
        Load the configuration from a file.
        
        Args:
            config_path (str, optional): Path to the configuration file. Defaults to None.
        
        Returns:
            Dict[str, Any]: Loaded configuration as a dictionary.
        
        Raises:
            FileNotFoundError: If no configuration file is found.
        """
        # If a config path is provided and exists, load it
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as config_file:
                return yaml.safe_load(config_file)

        # If no config path is provided, look for it in the user's home directory
        home_config = Path.home() / '.llmparty' / 'config.yaml'
        if home_config.exists():
            with open(home_config, 'r') as config_file:
                return yaml.safe_load(config_file)

        # If no config file is found, raise an error
        raise FileNotFoundError("Config file not found. Please run llmp-setup to create a config file.")

    def produce(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Produce output from the Language Model API with the given request.
        
        Args:
            request (Dict[str, Any]): Request parameters including provider, model, and prompt.
        
        Returns:
            Dict[str, Any]: API response parsed into a dictionary.
        
        Raises:
            ValueError: If the provider is unsupported or the response is invalid.
            RuntimeError: If the API call fails.
        """
        # Extract request parameters
        provider = request.get('provider', '').lower()
        model = request.get('model', '')
        prompt = request.get('prompt', '')

        # Check if the provider is supported
        if provider not in self.config:
            raise ValueError(f"Unsupported provider: {provider}")

        # Get the provider-specific configuration
        provider_config = self.config[provider]

        # Prepare the request parameters
        params = self._prepare_request(provider_config, model, prompt)

        # Prepare the curl command for the API call
        curl_command = self._prepare_curl_command(provider_config, params)

        # Execute the curl command
        result = subprocess.run(curl_command, capture_output=True, text=True)

        # Check if the API call was successful
        if result.returncode != 0:
            raise RuntimeError(f"API call failed: {result.stderr}")

        # Parse the JSON response
        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON response: {result.stdout}")

        # Parse and return the response
        return self._parse_response(provider_config, response)

    def _prepare_request(self, config: Dict[str, Any], model: str, prompt: str) -> Dict[str, Any]:
        """
        Prepare the request parameters based on the provider's configuration.
        
        Args:
            config (Dict[str, Any]): Provider-specific configuration.
            model (str): The model to use for the request.
            prompt (str): The prompt to send to the model.
        
        Returns:
            Dict[str, Any]: Prepared request parameters.
        """
        # Copy the request format from the configuration
        params = config['request_format'].copy()

        # Set the model
        params['model'] = model

        # Set the prompt based on the request format
        if 'messages' in params:
            params['messages'][0]['content'] = prompt
        elif 'prompt' in params:
            params['prompt'] = prompt

        return params

    def _prepare_curl_command(self, config: Dict[str, Any], params: Dict[str, Any]) -> list:
        """
        Prepare the curl command for the API call.
        
        Args:
            config (Dict[str, Any]): Provider-specific configuration.
            params (Dict[str, Any]): Prepared request parameters.
        
        Returns:
            list: Curl command as a list of strings.
        
        Raises:
            ValueError: If the API key is not set in the environment.
        """
        # Start with the basic curl command and API URL
        curl_command = ["curl", config['api_url']]

        # Add authentication header if required
        if config['auth_header']:
            api_key = os.getenv(config['api_key_env'])
            if not api_key:
                raise ValueError(f"API key for {config['auth_header']} is not set in environment variable {config['api_key_env']}")
            auth_value = f"{config['auth_prefix']} {api_key}" if config['auth_prefix'] else api_key
            curl_command.extend(["-H", f"{config['auth_header']}: {auth_value}"])

        # Add API version header if required
        if config.get('api_version_header') and config.get('api_version'):
            curl_command.extend(["-H", f"{config['api_version_header']}: {config['api_version']}"])

        # Add content type and request body
        curl_command.extend([
            "-H", f"Content-Type: {config['content_type']}",
            "-d", json.dumps(params)
        ])

        return curl_command

    def _parse_response(self, config: Dict[str, Any], response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the API response according to the provider's configuration.
        
        Args:
            config (Dict[str, Any]): Provider-specific configuration.
            response (Dict[str, Any]): Raw API response.
        
        Returns:
            Dict[str, Any]: Parsed response including content, token usage, and additional info.
        
        Raises:
            ValueError: If there's an error parsing the response.
        """
        try:
            # Extract the content from the response
            content = self._get_nested(response, config['response_parsing']['content_path'])

            # Extract usage statistics
            usage = {}
            for k, v in config['response_parsing']['usage_mapping'].items():
                if isinstance(v, list):
                    usage[k] = self._get_nested(response, v)
                elif isinstance(v, dict):  # Handle the case where it's a dict of lists
                    usage[k] = sum(self._get_nested(response, path) for path in v.values())
                else:
                    raise ValueError(f"Unexpected usage mapping format for {k}")
            
            # Ensure all usage values are integers or None
            usage = {k: int(v) if v is not None else None for k, v in usage.items()}
            
            # Calculate total_tokens if it's None or not provided
            if usage.get('total_tokens') is None:
                prompt_tokens = usage.get('prompt_tokens', 0) or 0
                completion_tokens = usage.get('completion_tokens', 0) or 0
                usage['total_tokens'] = prompt_tokens + completion_tokens
            
            # Determine which keys have been used in parsing
            used_keys = set()
            used_keys.update(self._get_all_keys(config['response_parsing']['content_path']))
            for path_list in config['response_parsing']['usage_mapping'].values():
                if isinstance(path_list, list):
                    used_keys.update(self._get_all_keys(path_list))
                elif isinstance(path_list, dict):
                    for path in path_list.values():
                        used_keys.update(self._get_all_keys(path))

            # Create the final output, excluding used keys
            output = {
                'content': json.loads(content.strip()),
                'token_usage': usage,
                'additional_info': {k: v for k, v in response.items() if k not in used_keys}
            }

            return output
        except (KeyError, TypeError, json.JSONDecodeError) as e:
            raise ValueError(f"Error parsing response: {str(e)}")

    def _get_nested(self, obj, path):
        """
        Get a nested value from a dictionary using a path.
        
        Args:
            obj: The dictionary to search in.
            path: A list representing the path to the nested value.
        
        Returns:
            The nested value if found, None otherwise.
        """
        for key in path:
            if isinstance(obj, dict):
                obj = obj.get(key, {})
            elif isinstance(obj, list) and isinstance(key, int):
                obj = obj[key] if 0 <= key < len(obj) else {}
            else:
                return None
        return obj

    def _get_all_keys(self, path):
        """
        Get all string keys from a path.
        
        Args:
            path: A list representing a path.
        
        Returns:
            set: A set of all string keys in the path.
        """
        return set(key for key in path if isinstance(key, str))

def main():
    """
    Main function to handle command-line interface for LLMParty.
    """
    # Set up command-line argument parser
    parser = argparse.ArgumentParser(description="LLMParty: Unified LLM API")
    parser.add_argument("-p", "--provider", required=True, help="LLM provider")
    parser.add_argument("-m", "--model", required=True, help="Model name")
    parser.add_argument("prompt", nargs="?", default=None, help="Prompt for the LLM")
    parser.add_argument("-u", "--show-usage", action="store_true", help="Show token usage statistics")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show additional information from the API response")
    parser.add_argument("--config", help="Path to the YAML configuration file")

    # Parse command-line arguments
    args = parser.parse_args()

    try:
        # Initialize LLMParty with the specified or default config
        llm_party = LLMParty(args.config)
    except FileNotFoundError as e:
        # If config file is not found, print error and exit
        print(json.dumps({"error": str(e)}))
        return

    # Check if the specified provider is supported
    if args.provider not in llm_party.config:
        print(json.dumps({"error": f"Unsupported provider '{args.provider}'. Available providers: {', '.join(llm_party.config.keys())}"}))
        return

    # Check if input is being piped in
    if not sys.stdin.isatty():
        prompt = sys.stdin.read().strip()
    elif args.prompt:
        prompt = args.prompt
    else:
        print(json.dumps({"error": "No prompt provided. Please provide a prompt as an argument or pipe it in."}))
        return

    # Prepare the request
    request = {
        "provider": args.provider,
        "model": args.model,
        "prompt": prompt
    }

    try:
        # Call the LLM API
        result = llm_party.produce(request)
        
        # Prepare the output
        output = result['content']
        
        # Include token usage if requested
        if args.show_usage:
            output["token_usage"] = result['token_usage']
        
        # Include additional info if verbose mode is on and additional info exists
        if args.verbose and result['additional_info']:
            output["additional_info"] = result['additional_info']
        
        # Print the output as JSON
        print(json.dumps(output, indent=2))
        
    except Exception as e:
        # If any error occurs, print it as JSON
        print(json.dumps({"error": str(e)}))

# If this script is run directly (not imported), run the main function
if __name__ == "__main__":
    main()
