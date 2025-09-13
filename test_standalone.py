# run_standalone.py - Test your backend independently
"""
Standalone testing setup for Member C's backend orchestration
Run this to test your Flask app without Member A/B's actual code
"""

import subprocess
import sys
import time
import requests
import json
from datetime import datetime

def install_dependencies():
    """Install required packages if not already installed"""
    required_packages = [
        'Flask==3.0.0',
        'Flask-CORS==4.0.0', 
        'requests==2.31.0',
        'python-dotenv==1.0.0'
    ]
    
    print("📦 Installing dependencies...")
    for package in required_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError:
            print(f"⚠️ Could not install {package}, continuing...")
    print("✅ Dependencies installed")

def create_env_file():
    """Create a basic .env file for testing"""
    env_content = """# Development environment variables
DEBUG=True
PORT=5000

# Mock API keys (replace with real ones later)
OPENWEATHER_API_KEY=your_api_key_here
GOOGLE_CLOUD_PROJECT=your_project_id

# Local testing URLs
FRONTEND_URL=http://localhost:3000
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
    except Exception as e:
        print(f"⚠️ Could not create .env file: {e}")

def test_flask_server():
    """Test if Flask server is running and responsive"""
    base_url = "http://localhost:5000"
    max_retries = 10
    
    print("🔍 Testing Flask server connectivity...")
    
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Flask server is responding")
                return True
        except requests.exceptions.ConnectionError:
            if attempt == 0:
                print("⏳ Waiting for Flask server to start...")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Error testing server: {e}")
            break
    
    print("❌ Flask server is not responding")
    return False

def run_basic_tests():
    """Run basic API tests with mock data"""
    base_url = "http://localhost:5000"
    
    test_queries = [
        {
            "query": "I'm visiting Turkey in October, what should I pack?",
            "description": "Basic travel packing query"
        },
        {
            "query": "Show me trending gifts for Eid in Dubai", 
            "description": "Cultural festival query"
        },
        {
            "query": "What should I wear for a business meeting in Japan?",
            "description": "Business travel query"
        },
        {
            "query": "",
            "description": "Empty query (should fail gracefully)",
            "expect_error": True
        }
    ]
    
    print("\n🧪 Running basic API tests...")
    print("=" * 60)
    
    passed = 0
    total = len(test_queries)
    
    for i, test in enumerate(test_queries, 1):
        print(f"\nTest {i}/{total}: {test['description']}")
        print(f"Query: '{test['query']}'")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/chat",
                json={"query": test["query"]},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            print(f"Response time: {response_time:.2f}s")
            
            if test.get("expect_error"):
                if response.status_code == 400:
                    print("✅ Correctly handled invalid input")
                    passed += 1
                else:
                    print(f"❌ Expected 400 error, got {response.status_code}")
            else:
                if response.status_code == 200:
                    data = response.json()
                    if "message" in data and "products" in data:
                        print("✅ Valid response structure")
                        print(f"Products returned: {len(data.get('products', []))}")
                        passed += 1
                    else:
                        print("❌ Invalid response structure")
                        print(f"Response: {json.dumps(data, indent=2)[:200]}...")
                else:
                    print(f"❌ Error response: {response.status_code}")
                    try:
                        error_data = response.json()
                        print(f"Error details: {error_data}")
                    except:
                        print(f"Raw response: {response.text[:200]}...")
                        
        except requests.exceptions.Timeout:
            print("❌ Request timeout (>30s)")
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    return passed == total

def run_performance_test():
    """Run a basic performance test"""
    base_url = "http://localhost:5000"
    query = "I'm visiting Paris in spring, what should I bring?"
    num_requests = 5
    
    print(f"\n⚡ Performance test: {num_requests} consecutive requests...")
    
    response_times = []
    
    for i in range(num_requests):
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/chat",
                json={"query": query},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                response_times.append(end_time - start_time)
                print(f"Request {i+1}: {response_times[-1]:.2f}s ✅")
            else:
                print(f"Request {i+1}: Failed ({response.status_code}) ❌")
                
        except Exception as e:
            print(f"Request {i+1}: Error - {e} ❌")
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        print(f"\n📈 Performance Results:")
        print(f"Average: {avg_time:.2f}s")
        print(f"Min: {min_time:.2f}s") 
        print(f"Max: {max_time:.2f}s")
        
        if avg_time < 3.0:
            print("✅ Performance target met (<3s average)")
        else:
            print("⚠️ Performance target not met (>3s average)")

def main():
    """Main testing workflow"""
    print("🚀 Backend Standalone Testing Setup")
    print("=" * 60)
    print("This will test your Flask backend with mock data")
    print("(No Member A/B code required)")
    print()
    
    # Step 1: Install dependencies
    install_dependencies()
    
    # Step 2: Create basic config
    create_env_file()
    
    # Step 3: Instructions to start server
    print("\n📋 Next Steps:")
    print("1. Save the Flask app code as 'app.py'")
    print("2. In another terminal, run: python app.py")
    print("3. Wait for 'Running on http://localhost:5000'")
    print("4. Press Enter here to continue testing...")
    input()
    
    # Step 4: Test server connectivity
    if not test_flask_server():
        print("\n❌ Cannot connect to Flask server")
        print("Make sure you've started the server with: python app.py")
        return
    
    # Step 5: Run API tests
    success = run_basic_tests()
    
    # Step 6: Performance test
    if success:
        run_performance_test()
    
    # Step 7: Summary
    print("\n🎯 Testing Summary")
    print("=" * 60)
    if success:
        print("✅ All tests passed! Your backend orchestration is working.")
        print("👥 Ready to integrate Member A/B code when available.")
        print("🎬 You can start recording demo footage with mock data.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        print("🔧 Debug and fix issues before integrating team code.")
    
    print("\n📝 Next Actions:")
    print("- Test frontend integration with this backend")
    print("- Create architecture diagram") 
    print("- Prepare demo script with current mock data")
    print("- Document integration points for Member A/B")

if __name__ == "__main__":
    main()