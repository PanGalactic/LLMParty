# setup.py

# Import necessary modules
import os  # For operating system dependent functionality
import shutil  # For high-level file operations
from pathlib import Path  # For object-oriented filesystem paths

def setup_llmparty():
    """
    Set up the LLMParty configuration directory and files.
    """
    # Get the user's home directory
    home_dir = Path.home()
    # Define the path for the LLMParty config directory
    llmp_dir = home_dir / '.llmparty'
    # Define the path for the config file
    config_file = llmp_dir / 'config.yaml'

    # Create the .llmparty directory if it doesn't exist
    if not llmp_dir.exists():
        llmp_dir.mkdir()
        print(f"Created directory: {llmp_dir}")

    # Copy config.yaml if it doesn't exist in .llmparty
    if not config_file.exists():
        # Assuming config.yaml is in the same directory as this script
        source_config = Path(__file__).parent / 'config.yaml'
        if source_config.exists():
            shutil.copy(source_config, config_file)
            print(f"Copied config file to: {config_file}")
        else:
            print(f"Error: Source config file not found at {source_config}")
    else:
        print(f"Config file already exists: {config_file}")

def main():
    """
    Main function to run the setup process.
    """
    # Call the setup function
    setup_llmparty()

# If this script is run directly (not imported), run the main function
if __name__ == "__main__":
    main()
