import requests
import time

def test_server():
    print("Testing server connection...")
    try:
        start_time = time.time()
        response = requests.get('http://localhost:8000/', timeout=10)
        end_time = time.time()
        
        print(f"✅ Server responded in {end_time - start_time:.2f} seconds")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused - server might not be running")
    except requests.exceptions.Timeout:
        print("❌ Request timed out - server is not responding")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_server()
