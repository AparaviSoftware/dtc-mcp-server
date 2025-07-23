"""Test direct connection to Aparavi API."""

import os
import json
from dotenv import load_dotenv
from integrations.aparavi.client import AparaviClient
from integrations.aparavi.exceptions import AparaviError

# Load environment variables
load_dotenv()

def test_aparavi_connection():
    """Test basic connection to Aparavi API."""
    
    # Get API credentials
    api_key = os.getenv("APARAVI_API_KEY")
    if not api_key:
        print("Error: APARAVI_API_KEY environment variable is required")
        return
    
    base_url = os.getenv("APARAVI_API_URL", "https://eaas-dev.aparavi.com")
    print(f"\nTesting connection to Aparavi API:")
    print(f"Base URL: {base_url}")
    
    # Initialize client
    client = AparaviClient(
        api_key=api_key,
        base_url=base_url
    )
    
    # Load test pipeline
    try:
        with open("resources/pipelines/simpleparser.json", 'r') as f:
            pipeline_data = json.load(f)
            
        pipeline_config = {
            "pipeline": {
                "source": "webhook_1",
                "components": pipeline_data["components"]
            }
        }

        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading pipeline configuration: {str(e)}")
        return

    try:
        # Step 1: Create task and wait for it to be ready
        print("\nStep 1: Creating and waiting for task...")
        task_token, ready_status = client.create_and_wait_for_task(
            pipeline=pipeline_config,
            name="Test Pipeline Task",
            type="gpu",
            max_retries=10,  # Increase retries
            initial_delay=2.0  # Start with longer delay
        )
        
        if ready_status.data and ready_status.data.get("serviceUp"):
            print("\n✓ Task ready and service is up!")
            if ready_status.data.get("notes"):
                print("Webhook URL:", ready_status.data["notes"][0])
        else:
            print("\n⚠ Task created but service may not be fully ready")
            
        print("Status:")
        print(json.dumps({
            "status": ready_status.status,
            "data": ready_status.data,
            "error": ready_status.error,
            "metrics": ready_status.metrics
        }, indent=2))

        # Step 2: Send test data
        print("\nStep 2: Sending test data...")
        result = client.post_to_webhook(
            token=task_token,
            data={
                "content": "This is a test document.",
                "filename": "test.txt"
            },
            type="gpu"
        )
        print("✓ Data sent successfully!")
        print("Response:")
        print(json.dumps(result, indent=2))

        # Step 3: Final status check
        print("\nStep 3: Final status check...")
        result = client.get_task_status(task_token, type="gpu")
        print("✓ Final status:")
        print(json.dumps({
            "status": result.status,
            "data": result.data,
            "error": result.error,
            "metrics": result.metrics
        }, indent=2))

    except AparaviError as e:
        print(f"\n✗ Error during task execution: {str(e)}")
        if "not found" in str(e).lower():
            print("\nPossible causes:")
            print("- Task initialization failed")
            print("- Task was cleaned up too quickly")
            print("- Service is under heavy load")
            print("\nSuggestions:")
            print("- Try increasing max_retries and initial_delay")
            print("- Check service status")
        return

if __name__ == "__main__":
    test_aparavi_connection()