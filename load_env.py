"""
Environment Variable Loader for Elizabeth_PI
Automatically loads environment variables from .env file
Call this at the start of any script that needs API keys
"""

import os
from pathlib import Path


def load_env_file(env_path=None, silent=False):
    """Load environment variables from .env file"""
    # Check if we've already loaded the env file
    if os.environ.get('_ENV_FILE_LOADED'):
        return True
    
    if env_path is None:
        # Look for .env file in the current directory and parent directories
        current_dir = Path(__file__).parent
        env_path = current_dir / '.env'
        
        # If not found, try parent directories
        if not env_path.exists():
            for parent in current_dir.parents:
                potential_env = parent / '.env'
                if potential_env.exists():
                    env_path = potential_env
                    break
    
    if not env_path or not Path(env_path).exists():
        if not silent:
            print(f"⚠️ No .env file found. API keys may not be available.")
        return False
    
    try:
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        loaded_vars = []
        for line in lines:
            line = line.strip()
            # Skip comments and empty lines
            if line.startswith('#') or not line or '=' not in line:
                continue
            
            # Parse key=value pairs
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")  # Remove quotes
            
            # Set environment variable
            os.environ[key] = value
            loaded_vars.append(key)
        
        # Mark that we've loaded the env file
        os.environ['_ENV_FILE_LOADED'] = '1'
        
        if loaded_vars and not silent:
            print(f"✅ Loaded environment variables: {', '.join(loaded_vars)}")
        return True
        
    except Exception as e:
        print(f"❌ Error loading .env file: {e}")
        return False


def ensure_api_key():
    """Ensure OpenAI API key is available"""
    # First try to load from .env file
    load_env_file()
    
    # Check if API key is now available
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"🔑 OpenAI API key loaded: {api_key[:15]}...")
        return True
    else:
        print("❌ No OpenAI API key found in environment or .env file")
        print("💡 Create a .env file with: OPENAI_API_KEY=\"your_key_here\"")
        return False


# Auto-load when this module is imported
if __name__ != "__main__":
    load_env_file()


if __name__ == "__main__":
    print("🔧 Environment Variable Loader for Elizabeth_PI")
    print("=" * 50)
    
    # Test loading
    success = load_env_file()
    if success:
        print("\n📋 Current environment variables:")
        for key in os.environ:
            if 'API' in key or 'KEY' in key:
                value = os.environ[key]
                masked_value = value[:10] + "..." if len(value) > 10 else value
                print(f"  {key}: {masked_value}")
    
    # Test API key specifically
    print("\n🧪 Testing API key availability:")
    ensure_api_key()