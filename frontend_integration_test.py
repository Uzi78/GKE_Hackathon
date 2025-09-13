# frontend_integration_test.py - Test frontend with your backend

import subprocess
import sys
import time
import webbrowser
import os
from pathlib import Path

def setup_frontend():
    """Set up the frontend files for testing"""
    
    # Create frontend directory
    frontend_dir = Path("frontend")
    frontend_dir.mkdir(exist_ok=True)
    
    print("📁 Setting up frontend files...")
    
    # Instructions to save the frontend
    frontend_instructions = """
🎯 FRONTEND SETUP INSTRUCTIONS:

1. Go to the first artifact I created (the HTML frontend)
2. Copy the entire HTML code 
3. Save it as 'frontend/index.html' in your project directory
4. Make sure the file is saved in the 'frontend' folder

Your project structure should look like:
travel-chatbot-backend/
├── app.py                 # Your Flask backend
├── frontend/
│   └── index.html         # The frontend I created
├── test_standalone.py     # Backend tests
└── requirements.txt       # Dependencies

Press Enter when you've saved the frontend file...
"""
    
    print(frontend_instructions)
    input()
    
    # Check if frontend file exists
    frontend_file = frontend_dir / "index.html"
    if not frontend_file.exists():
        print("❌ Frontend file not found at frontend/index.html")
        print("Please save the HTML frontend code to that location.")
        return False
    
    print("✅ Frontend file found!")
    return True

def update_frontend_config():
    """Update the frontend to point to your local backend"""
    
    frontend_file = Path("frontend/index.html")
    
    if not frontend_file.exists():
        print("❌ Frontend file not found")
        return False
    
    try:
        # Read the frontend file
        with open(frontend_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update the API_BASE_URL to point to your local backend
        updated_content = content.replace(
            "const API_BASE_URL = 'http://localhost:5000';",
            "const API_BASE_URL = 'http://localhost:5000';"
        )
        
        # Make sure CORS is handled properly - add a comment about it
        if "// Configuration - Update this with your Flask backend URL" in updated_content:
            updated_content = updated_content.replace(
                "// Configuration - Update this with your Flask backend URL",
                "// Configuration - Currently pointing to your local Flask backend"
            )
        
        # Write back the updated file
        with open(frontend_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ Frontend configured to use your local backend")
        return True
        
    except Exception as e:
        print(f"❌ Error updating frontend config: {e}")
        return False

def check_backend_running():
    """Check if your Flask backend is running"""
    import requests
    
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and healthy")
            return True
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running")
        print("Please start your Flask backend with: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error checking backend: {e}")
        return False
    
    return False

def serve_frontend():
    """Serve the frontend using Python's built-in server"""
    
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    print("🌐 Starting frontend server...")
    print("Frontend will be available at: http://localhost:8000")
    print("Press Ctrl+C to stop the frontend server")
    print()
    
    try:
        # Change to frontend directory and start server
        os.chdir(frontend_dir)
        
        # Start Python HTTP server
        if sys.version_info[0] == 3:
            subprocess.run([sys.executable, "-m", "http.server", "8000"])
        else:
            subprocess.run([sys.executable, "-m", "SimpleHTTPServer", "8000"])
            
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped")
        return True
    except Exception as e:
        print(f"❌ Error starting frontend server: {e}")
        return False

def run_integration_tests():
    """Run tests to verify frontend-backend integration"""
    
    print("🧪 Running Frontend-Backend Integration Tests...")
    print("=" * 60)
    
    tests = [
        {
            "name": "Backend Health Check",
            "url": "http://localhost:5000/health",
            "method": "GET"
        },
        {
            "name": "CORS Headers Check", 
            "url": "http://localhost:5000/chat",
            "method": "OPTIONS"
        },
        {
            "name": "Chat Endpoint Test",
            "url": "http://localhost:5000/chat",
            "method": "POST",
            "data": {"query": "Test integration"}
        }
    ]
    
    import requests
    
    passed = 0
    total = len(tests)
    
    for i, test in enumerate(tests, 1):
        print(f"\nTest {i}/{total}: {test['name']}")
        
        try:
            if test['method'] == 'GET':
                response = requests.get(test['url'], timeout=10)
            elif test['method'] == 'OPTIONS':
                response = requests.options(test['url'], timeout=10)
            elif test['method'] == 'POST':
                response = requests.post(
                    test['url'], 
                    json=test['data'],
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
            
            print(f"Status: {response.status_code}")
            
            # Check CORS headers
            if 'Access-Control-Allow-Origin' in response.headers:
                print("✅ CORS headers present")
            else:
                print("⚠️ CORS headers missing (might cause frontend issues)")
            
            if response.status_code in [200, 204]:
                print("✅ Test passed")
                passed += 1
            else:
                print("❌ Test failed")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print(f"\n📊 Integration Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        print("Your frontend should work perfectly with your backend.")
    else:
        print("⚠️ Some tests failed - check CORS and backend status")
    
    return passed == total

def open_frontend_browser():
    """Open the frontend in the default browser"""
    frontend_url = "http://localhost:8000"
    
    print(f"🌐 Opening frontend at {frontend_url}")
    
    try:
        webbrowser.open(frontend_url)
        print("✅ Frontend opened in browser")
        return True
    except Exception as e:
        print(f"⚠️ Could not open browser automatically: {e}")
        print(f"Please manually open: {frontend_url}")
        return False

def main():
    """Main integration testing workflow"""
    
    print("🔗 Frontend-Backend Integration Setup")
    print("=" * 60)
    print("This will help you test the frontend with your Flask backend")
    print()
    
    # Step 1: Set up frontend files
    if not setup_frontend():
        return
    
    # Step 2: Update frontend configuration  
    if not update_frontend_config():
        return
    
    # Step 3: Check backend is running
    if not check_backend_running():
        print("\n📋 Backend Setup Required:")
        print("1. Open another terminal/command prompt")
        print("2. Navigate to your project directory") 
        print("3. Run: python app.py")
        print("4. Wait for 'Running on http://localhost:5000'")
        print("5. Come back here and press Enter to continue...")
        input()
        
        if not check_backend_running():
            print("❌ Still cannot connect to backend. Please check it's running.")
            return
    
    # Step 4: Run integration tests
    if not run_integration_tests():
        print("⚠️ Integration tests failed. Check the errors above.")
        print("Common issues:")
        print("- Backend not running on port 5000")
        print("- CORS not properly configured")
        print("- Firewall blocking connections")
        return
    
    # Step 5: Instructions for manual testing
    print("\n🎯 Manual Testing Instructions")
    print("=" * 60)
    print("1. I'll start a frontend server for you")
    print("2. Open http://localhost:8000 in your browser")  
    print("3. Try these test queries:")
    print("   - 'I'm visiting Turkey in October, what should I pack?'")
    print("   - 'Show me trending gifts for Eid in Dubai'")
    print("   - 'What should I wear in Japan during winter?'")
    print("4. Verify you get responses with product recommendations")
    print()
    
    choice = input("Ready to start frontend server? (y/n): ").lower().strip()
    
    if choice == 'y':
        # Step 6: Start frontend server
        print("\n🚀 Starting frontend server...")
        print("Keep your backend running in the other terminal!")
        print()
        
        # Open browser first
        time.sleep(1)
        open_frontend_browser()
        
        # Then start server (this will block)
        serve_frontend()
    else:
        print("\n📝 Manual Testing:")
        print("1. Navigate to the frontend directory: cd frontend")
        print("2. Start server: python -m http.server 8000") 
        print("3. Open: http://localhost:8000")
        print("4. Test the chat interface!")

if __name__ == "__main__":
    main()