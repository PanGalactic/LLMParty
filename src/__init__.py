# __init__.py

# Import the main LLMParty class from the main module
from .main import LLMParty

# Import the setup function from the setup module
from .setup import setup_llmparty

# Define what should be imported when using "from llmparty import *"
__all__ = ['LLMParty', 'setup_llmparty']

# Define the version of the package
__version__ = '0.1.0'
