"""Test direct connection to Aparavi API."""

import os
import json
import tempfile
from dotenv import load_dotenv
from integrations.aparavi.client import AparaviClient
from integrations.aparavi.exceptions import AparaviError

def test_aparavi_connection():
    """Test basic connection and API functionality."""

    # Load environment variables
    load_dotenv()
    api_key = os.getenv('APARAVI_API_KEY')
    api_url = os.getenv('APARAVI_API_URL', 'https://eaas-dev.aparavi.com')

    if not api_key:
        print("⚠ APARAVI_API_KEY not found in environment")
        return

    print("\nTesting Aparavi API connection:")
    print(f"- API URL: {api_url}")

    # Initialize client
    client = AparaviClient(
        base_url=api_url,
        api_key=api_key,
        timeout=120,
        logs="verbose"
    )

    # Load test pipeline configuration
    package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pipeline_config_path = os.path.join(package_root, "resources", "pipelines", "simpleparser.json")

    if not os.path.exists(pipeline_config_path):
        print(f"⚠ Pipeline configuration not found at: {pipeline_config_path}")
        return

    with open(pipeline_config_path, 'r') as f:
        pipeline_data = json.load(f)

    pipeline_config = {
        "pipeline": {
            "source": "webhook_1",
            "components": pipeline_data["components"]
        }
    }

    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp:
        temp.write("This is a test document for Aparavi API.\n")
        temp.write("It contains some sample text to process.\n")
        temp_path = temp.name

    try:
        print("\nStarting API test sequence...")

        # Create task and get server-assigned type
        task_token, task_type, ready_status = client.create_and_wait_for_task(
            pipeline=pipeline_config,
            name="API Connection Test",
            threads=None
        )

        print("\nTask ready:")
        print(f"- Token: {task_token}")
        print(f"- Type: {task_type}")
        if ready_status.data and ready_status.data.get("notes"):
            print(f"- Webhook URL: {ready_status.data['notes'][0]}")

        # Send test file to webhook using server-assigned type
        print("\nSending test file to webhook...")
        responses = client.send_payload_to_webhook(
            token=task_token,
            task_type=task_type,
            file_glob=temp_path
        )

        # Process webhook response
        if responses and responses[0].get('status') == 'OK':
            result = responses[0]
            print("\n✓ File processed successfully")
            print("\nProcessing result:")
            print(json.dumps(result, indent=2))

            # Extract and display text content if available
            if result.get('data', {}).get('objects'):
                first_object = next(iter(result['data']['objects'].values()))
                if first_object.get('text'):
                    print("\nExtracted text:")
                    print(first_object['text'][0])
        else:
            print("\n⚠ Processing failed or returned no results")

        # End the task
        print("\nEnding task...")
        client.end_task(token=task_token, task_type=task_type)
        print("✓ Task ended successfully")

    except AparaviError as e:
        print(f"\n⚠ Aparavi API error: {e}")
    except Exception as e:
        print(f"\n⚠ Unexpected error: {e}")
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_path)
        except OSError:
            pass

if __name__ == "__main__":
    test_aparavi_connection()
