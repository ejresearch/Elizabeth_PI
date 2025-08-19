"""
API Key Management Utility for Lizzy Framework
Handles OpenAI API key storage, validation, and testing
"""

import os
import json
import asyncio
import getpass
from datetime import datetime
from typing import Optional, Dict, Any

# Auto-load environment variables from .env file
try:
    from load_env import load_env_file
    load_env_file()
except ImportError:
    pass

class APIKeyManager:
    """Manages OpenAI API key storage and validation"""
    
    def __init__(self, config_file: str = "api_config.json"):
        self.config_file = config_file
        self.config_data = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load API configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"api_keys": {}, "last_validated": {}}
    
    def save_config(self):
        """Save API configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config_data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save API config: {e}")
    
    def set_openai_key(self, api_key: str) -> bool:
        """Set and store OpenAI API key"""
        if not api_key or not api_key.startswith('sk-'):
            print("❌ Invalid API key format. OpenAI keys start with 'sk-'")
            return False
        
        # Store in config
        self.config_data["api_keys"]["openai"] = api_key
        self.save_config()
        
        # Set in environment for current session
        os.environ['OPENAI_API_KEY'] = api_key
        
        print("✅ OpenAI API key stored successfully")
        return True
    
    def get_openai_key(self) -> Optional[str]:
        """Get OpenAI API key from config or environment"""
        # Check environment first
        env_key = os.getenv('OPENAI_API_KEY')
        if env_key:
            return env_key
        
        # Check stored config
        return self.config_data.get("api_keys", {}).get("openai")
    
    def test_openai_key(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Test OpenAI API key with actual API call"""
        if not api_key:
            api_key = self.get_openai_key()
        
        if not api_key:
            return {
                "success": False,
                "error": "No API key found",
                "details": "Please set an OpenAI API key first"
            }
        
        try:
            from openai import OpenAI
            
            print("🔍 Testing OpenAI API key...")
            client = OpenAI(api_key=api_key)
            
            # Test with embedding API (cheaper than completions)
            response = client.embeddings.create(
                model='text-embedding-ada-002',
                input='API key test'
            )
            
            # Test with a small completion
            completion = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[{"role": "user", "content": "Say 'API test successful' in exactly 3 words."}],
                max_tokens=10
            )
            
            result = {
                "success": True,
                "embedding_test": True,
                "completion_test": True,
                "embedding_dimensions": len(response.data[0].embedding),
                "completion_response": completion.choices[0].message.content.strip(),
                "tested_at": datetime.now().isoformat()
            }
            
            # Store successful validation
            self.config_data["last_validated"]["openai"] = result["tested_at"]
            self.save_config()
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            return {
                "success": False,
                "error": "API call failed",
                "details": error_msg,
                "tested_at": datetime.now().isoformat()
            }
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get current API key status"""
        openai_key = self.get_openai_key()
        last_validated = self.config_data.get("last_validated", {}).get("openai")
        
        return {
            "openai_key_present": bool(openai_key),
            "openai_key_format_valid": openai_key.startswith('sk-') if openai_key else False,
            "last_validated": last_validated,
            "key_preview": f"{openai_key[:10]}..." if openai_key else None
        }
    
    def interactive_setup(self):
        """Interactive API key setup"""
        print("\n" + "="*60)
        print("🔑 API KEY MANAGEMENT")
        print("="*60)
        
        # Show current status
        status = self.get_api_status()
        
        if status["openai_key_present"]:
            print(f"📋 Current OpenAI API key: {status['key_preview']}")
            if status["last_validated"]:
                print(f"✅ Last validated: {status['last_validated']}")
            else:
                print("⚠️  Key not validated yet")
        else:
            print("❌ No OpenAI API key configured")
        
        print("\nOptions:")
        print("1. Set new OpenAI API key")
        print("2. Test current API key")
        print("3. Show API key status")
        print("4. Back to main menu")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "1":
            print("\n🔐 Enter your OpenAI API key:")
            print("💡 Get one from: https://platform.openai.com/account/api-keys")
            api_key = getpass.getpass("API Key (hidden): ").strip()
            
            if self.set_openai_key(api_key):
                print("\n🧪 Testing API key...")
                result = self.test_openai_key(api_key)
                self.display_test_result(result)
        
        elif choice == "2":
            result = self.test_openai_key()
            self.display_test_result(result)
        
        elif choice == "3":
            self.display_status()
        
        elif choice == "4":
            return
        
        else:
            print("❌ Invalid choice")
    
    def display_test_result(self, result: Dict[str, Any]):
        """Display API key test results"""
        print("\n" + "="*50)
        print("🧪 API KEY TEST RESULTS")
        print("="*50)
        
        if result["success"]:
            print("🎉 SUCCESS! Your OpenAI API key is working perfectly!")
            print(f"✅ Embedding test: Passed ({result.get('embedding_dimensions', 'N/A')} dimensions)")
            print(f"✅ Completion test: Passed")
            print(f"💬 Test response: '{result.get('completion_response', 'N/A')}'")
            print(f"🕒 Tested at: {result['tested_at']}")
            print("\n🚀 You're ready to build knowledge graphs!")
        else:
            print("❌ FAILED! There's an issue with your API key:")
            print(f"🚫 Error: {result['error']}")
            print(f"📝 Details: {result['details']}")
            print("\n💡 Solutions:")
            print("  • Get a new API key from https://platform.openai.com/account/api-keys")
            print("  • Check if your account has available credits")
            print("  • Verify the key was copied correctly")
    
    def display_status(self):
        """Display current API configuration status"""
        print("\n" + "="*50)
        print("📊 API KEY STATUS")
        print("="*50)
        
        status = self.get_api_status()
        
        print(f"OpenAI API Key:")
        if status["openai_key_present"]:
            print(f"  ✅ Present: {status['key_preview']}")
            print(f"  ✅ Format: {'Valid' if status['openai_key_format_valid'] else 'Invalid'}")
        else:
            print(f"  ❌ Not configured")
        
        if status["last_validated"]:
            print(f"  ✅ Last validated: {status['last_validated']}")
        else:
            print(f"  ⚠️  Never validated")
        
        print(f"\nEnvironment variable: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")


def main():
    """Main function for standalone testing"""
    manager = APIKeyManager()
    manager.interactive_setup()

if __name__ == "__main__":
    main()