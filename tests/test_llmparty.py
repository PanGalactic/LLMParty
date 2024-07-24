# test_llmparty.py

# Import the unittest module for creating and running tests
import unittest

# Import the LLMParty class from our package
from llmparty import LLMParty

class TestLLMParty(unittest.TestCase):
    def setUp(self):
        """
        Set up a new LLMParty instance before each test.
        This method is called before each test method.
        """
        # Create a new instance of LLMParty for each test
        self.llm_party = LLMParty()

    def test_initialization(self):
        """
        Test that the LLMParty is initialized with a configuration.
        """
        # Assert that the config attribute is not None
        self.assertIsNotNone(self.llm_party.config)

    def test_load_config(self):
        """
        Test the load_config method.
        """
        # Load a config (this will use the default path if no argument is provided)
        config = self.llm_party.load_config()
        # Assert that the loaded config is a dictionary
        self.assertIsInstance(config, dict)
        # Assert that the config contains expected keys (adjust based on your actual config)
        self.assertIn('openai', config)
        self.assertIn('anthropic', config)

    def test_prepare_request(self):
        """
        Test the _prepare_request method.
        """
        # Create a mock config
        mock_config = {
            'request_format': {
                'model': 'test_model',
                'messages': [{'role': 'user', 'content': 'test_prompt'}]
            }
        }
        # Prepare a request
        request = self.llm_party._prepare_request(mock_config, 'gpt-3.5-turbo', 'Hello, world!')
        # Assert that the request contains the expected keys and values
        self.assertEqual(request['model'], 'gpt-3.5-turbo')
        self.assertEqual(request['messages'][0]['content'], 'Hello, world!')

    def test_prepare_curl_command(self):
        """
        Test the _prepare_curl_command method.
        """
        # Create a mock config
        mock_config = {
            'api_url': 'https://api.example.com',
            'auth_header': 'Authorization',
            'auth_prefix': 'Bearer',
            'api_key_env': 'TEST_API_KEY',
            'content_type': 'application/json'
        }
        # Create mock params
        mock_params = {'model': 'test-model', 'prompt': 'Hello, world!'}
        # Set a mock environment variable
        import os
        os.environ['TEST_API_KEY'] = 'test_key_12345'
        # Prepare the curl command
        curl_command = self.llm_party._prepare_curl_command(mock_config, mock_params)
        # Assert that the curl command is correctly formatted
        self.assertEqual(curl_command[0], 'curl')
        self.assertEqual(curl_command[1], 'https://api.example.com')
        self.assertIn('-H', curl_command)
        self.assertIn('Authorization: Bearer test_key_12345', curl_command)

    def test_get_nested(self):
        """
        Test the _get_nested method.
        """
        # Create a nested dictionary
        nested_dict = {'a': {'b': {'c': 'value'}}}
        # Test getting a nested value
        result = self.llm_party._get_nested(nested_dict, ['a', 'b', 'c'])
        self.assertEqual(result, 'value')
        # Test getting a non-existent nested value
        result = self.llm_party._get_nested(nested_dict, ['a', 'b', 'd'])
        self.assertIsNone(result)

    def test_get_all_keys(self):
        """
        Test the _get_all_keys method.
        """
        # Create a test path
        test_path = ['a', 0, 'b', 1, 'c']
        # Get all string keys
        result = self.llm_party._get_all_keys(test_path)
        # Assert that only string keys are returned
        self.assertEqual(result, {'a', 'b', 'c'})

# If this script is run directly (not imported), run the tests
if __name__ == '__main__':
    unittest.main()
