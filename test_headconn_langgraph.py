import os
from headconn import Headconn

def test_headconn():
    print("Starting Headconn test...")
    headconn = Headconn()
    
    # Use a simple prompt
    prompt = "A futuristic city with flying cars"
    
    print(f"Running with prompt: {prompt}")
    result = headconn.run(prompt)
    
    print("Result:", result)
    
    if result.get('error'):
        print(f"Test Failed: {result['error']}")
    elif result.get('final_image'):
        print(f"Test Passed! Final image: {result['final_image']}")
        # Check if file exists
        if os.path.exists(f"tmp/{result['final_image']}"):
             print("Final image file exists.")
        else:
             print("Final image file NOT found.")
    else:
        print("Test Inconclusive.")

if __name__ == "__main__":
    test_headconn()
