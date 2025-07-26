"""
Aparavi Client for MCP Server
"""

import sys
import time
import requests
import glob
import os
import mimetypes
import json
from typing import Optional, Dict, Any, Tuple, List
from .models import ResultBase
from .exceptions import AparaviError, AuthenticationError, ValidationError, TaskNotFoundError, PipelineError, TaskTimeoutError


class AparaviClient:
    """
    Client for interacting with Aparavi Web Services API
    """
    
    COLOR_ORANGE = "\033[93m"
    COLOR_GREEN = "\033[92m"
    
    def __init__(self, base_url: str = "https://eaas-dev.aparavi.com", api_key: str = None, timeout: int = 120, logs: str = "verbose"):
        """
        Initialize the Aparavi client
        
        Args:
            base_url: The base URL of the Aparavi API
            api_key: The API key for authentication
            timeout: Request timeout in seconds (default: 30)
            logs: Logging level ("none", "normal", "verbose")
        """
        print("\nInitializing Aparavi client:", file=sys.stderr)
        print(f"- Base URL: {base_url}", file=sys.stderr)
        print(f"- Timeout: {timeout} seconds", file=sys.stderr)
        
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.logs = logs
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })

    def _log(self, message: str, color: str = ""):
        """Internal logging helper"""
        print(f"{color}{message}\033[0m", file=sys.stderr)

    def send_payload_to_webhook(self, token: str, task_type: str, file_glob: str) -> List[Dict[str, Any]]:
        """Send file(s) to the webhook endpoint.
        
        Args:
            token: The task token
            task_type: Type of processing as returned by the server
            file_glob: Glob pattern to match files to send
            
        Returns:
            List[Dict[str, Any]]: List of responses from the webhook
            
        Raises:
            ValueError: If no files match the glob pattern
            AparaviError: For API errors
        """
        file_paths = glob.glob(file_glob)
        if not file_paths:
            raise ValueError(f"No files matched pattern: {file_glob}")

        webhook_url = f"{self.base_url}/webhook"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        responses = []

        try:
            if len(file_paths) > 1:
                files_to_upload = []
                for file_path in file_paths:
                    with open(file_path, "rb") as f:
                        file_buffer = f.read()
                    filename = os.path.basename(file_path)
                    content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
                    files_to_upload.append(
                        ("files", (filename, file_buffer, content_type))
                    )

                if self.logs != "none":
                    self._log(f"Uploading {len(files_to_upload)} files to webhook (multipart)", self.COLOR_ORANGE)

                response = requests.put(
                    webhook_url,
                    params={"token": token, "type": task_type},
                    headers=headers,
                    files=files_to_upload,
                    timeout=self.timeout,
                )

            else:
                file_path = file_paths[0]
                with open(file_path, "rb") as f:
                    file_buffer = f.read()
                filename = os.path.basename(file_path)
                content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

                if self.logs != "none":
                    self._log(f"Uploading single file to webhook: {filename}", self.COLOR_ORANGE)

                headers.update({
                    "Content-Type": content_type,
                    "Content-Disposition": f'attachment; filename="{filename}"',
                })

                response = requests.put(
                    webhook_url,
                    params={"token": token, "type": task_type},
                    headers=headers,
                    data=file_buffer,
                    timeout=self.timeout,
                )

            response.raise_for_status()

            response_json = response.json()
            responses.append(response_json)

            if self.logs == "verbose":
                self._log(f"Webhook response:\n{json.dumps(response_json, indent=2)}", self.COLOR_GREEN)

            return responses

        except requests.exceptions.RequestException as e:
            if e.response:
                raise AparaviError(
                    f"Webhook failed: Server responded with status {e.response.status_code} - {e.response.text}"
                )
            raise AparaviError(f"Error sending to webhook: {e}")

    def wait_for_task_ready(
        self, 
        task_token: str,
        task_type: str,
        max_retries: int = 10,
        initial_delay: float = 2.0,
        timeout: Optional[float] = None
    ) -> Tuple[bool, ResultBase]:
        """
        Wait for a task to be ready with exponential backoff
        
        Args:
            task_token: The task token to check
            task_type: Type of processing as returned by the server
            max_retries: Maximum number of retries
            initial_delay: Initial delay in seconds
            timeout: Maximum total time to wait in seconds
            
        Returns:
            Tuple[bool, ResultBase]: (is_ready, last_status)
            
        Raises:
            TaskTimeoutError: If timeout is reached
            TaskNotFoundError: If task is not found after retries
            AparaviError: For other API errors
        """
        print("\nWaiting for task to be ready:", file=sys.stderr)
        print(f"- Token: {task_token}", file=sys.stderr)
        print(f"- Type: {task_type}", file=sys.stderr)
        print(f"- Max retries: {max_retries}", file=sys.stderr)
        print(f"- Initial delay: {initial_delay} seconds", file=sys.stderr)
        print(f"- Timeout: {timeout if timeout else 'None'} seconds", file=sys.stderr)

        delay = initial_delay
        start_time = time.time()
        last_status = None

        # Initial wait to let task initialize
        print(f"\nWaiting {delay} seconds for initial task setup...", file=sys.stderr)
        time.sleep(delay)

        for attempt in range(max_retries):
            if timeout and (time.time() - start_time) > timeout:
                print(f"\n⚠ Task {task_token} timed out after {timeout} seconds", file=sys.stderr)
                raise TaskTimeoutError(f"Task {task_token} failed to become ready within {timeout} seconds")

            print(f"\nChecking task status (attempt {attempt + 1}/{max_retries})...", file=sys.stderr)
            
            try:
                result = self.get_task_status(task_token, task_type)
                last_status = result

                # Check if service is up and ready
                if result.data and result.data.get("serviceUp"):
                    print("\n✓ Task ready and service is up!", file=sys.stderr)
                    if result.data.get("notes"):
                        print("Webhook URL:", result.data["notes"][0], file=sys.stderr)
                    return True, result
                else:
                    print("\n⚠ Service not ready yet", file=sys.stderr)
                
            except TaskNotFoundError:
                print(f"\n⚠ Task {task_token} not found on attempt {attempt + 1}", file=sys.stderr)
                result = None
                
            except Exception as e:
                print(f"\n✗ Error checking task status: {str(e)}", file=sys.stderr)
                raise AparaviError(f"Error checking task status: {str(e)}")

            # If we get here and it's the last attempt, raise appropriate error
            if attempt == max_retries - 1:
                if result is None:
                    print(f"\n✗ Task {task_token} not found after {max_retries} attempts", file=sys.stderr)
                    raise TaskNotFoundError(f"Task {task_token} not found after {max_retries} attempts")
                print(f"\n⚠ Task not ready after {max_retries} attempts", file=sys.stderr)
                return False, last_status

            # Not the last attempt, wait and continue
            delay += 2  # Double the delay for next attempt
            print(f"\nWaiting {delay} seconds before next check...", file=sys.stderr)
            time.sleep(delay)

        return False, last_status

    def execute_pipeline(
        self,
        pipeline: Dict[str, Any],
        name: Optional[str] = None,
        threads: Optional[int] = None
    ) -> Tuple[str, str]:
        """
        Execute a pipeline and return its token and type.
        
        Args:
            pipeline: The pipeline configuration
            name: Optional name for the task
            threads: Optional number of threads (1-16)
            
        Returns:
            Tuple[str, str]: (task_token, task_type) as determined by the server
            
        Raises:
            ValidationError: If pipeline validation fails
            AparaviError: For other API errors
        """
        print("\nCreating new task:", file=sys.stderr)
        print(f"- Name: {name if name else 'default'}", file=sys.stderr)
        print(f"- Threads: {threads if threads else 'default'}", file=sys.stderr)
        
        # First validate the pipeline
        print("\nValidating pipeline configuration...", file=sys.stderr)
        self.validate_pipe(pipeline)
        print("✓ Pipeline validation successful", file=sys.stderr)
        
        # Create the task
        params = {}
        if name:
            params['name'] = name
        if threads:
            if not 1 <= threads <= 16:
                raise ValueError("Threads must be between 1 and 16")
            params['threads'] = threads
        
        response = self._make_request(
            method='PUT',
            endpoint='/task',
            json=pipeline,
            params=params
        )
        
        result = ResultBase(
            status=response['status'],
            data=response.get('data'),
            error=response.get('error'),
            metrics=response.get('metrics')
        )
        
        if result.status == 'Error':
            print(f"✗ Task execution failed: {result.error}", file=sys.stderr)
            raise AparaviError(f"Task execution failed: {result.error}")
        
        if not result.data or 'token' not in result.data or 'type' not in result.data:
            raise AparaviError("Server response missing required token or type")
            
        task_token = result.data['token']
        task_type = result.data['type']
        
        print("\n✓ Task created successfully:", file=sys.stderr)
        print(f"- Token: {task_token}", file=sys.stderr)
        print(f"- Type: {task_type}", file=sys.stderr)
        
        return task_token, task_type

    def create_and_wait_for_task(
        self,
        pipeline: Dict[str, Any],
        name: Optional[str] = None,
        threads: Optional[int] = None,
        max_retries: int = 10,
        initial_delay: float = 2.0,
        timeout: Optional[float] = None
    ) -> Tuple[str, str, ResultBase]:
        """
        Create a task and wait for it to be ready
        
        Args:
            pipeline: The pipeline configuration
            name: Optional name for the task
            threads: Optional number of threads (1-16)
            max_retries: Maximum number of retries for status check
            initial_delay: Initial delay for status check
            timeout: Maximum total time to wait
            
        Returns:
            Tuple[str, str, ResultBase]: (task_token, task_type, ready_status)
            
        Raises:
            ValidationError: If pipeline validation fails
            TaskTimeoutError: If task fails to become ready
            AparaviError: For other API errors
        """
        # Create the task and get its token and type
        task_token, task_type = self.execute_pipeline(pipeline, name, threads)
        
        print("\nWaiting for service to be ready...", file=sys.stderr)
        
        # Wait for task to be ready using the server-provided type
        is_ready, status = self.wait_for_task_ready(
            task_token=task_token,
            task_type=task_type,
            max_retries=max_retries,
            initial_delay=initial_delay,
            timeout=timeout
        )
        
        if not is_ready:
            print(f"\n✗ Task {task_token} failed to become ready", file=sys.stderr)
            raise TaskTimeoutError(f"Task {task_token} failed to become ready after {max_retries} attempts")
            
        return task_token, task_type, status
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an HTTP request to the API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            Dict containing the API response
            
        Raises:
            AuthenticationError: If authentication fails
            ValidationError: If validation fails
            TaskNotFoundError: If task is not found
            AparaviError: For other API errors
        """
        url = f"{self.base_url}{endpoint}"
        
        print("\nMaking API request:", file=sys.stderr)
        print(f"- Method: {method}", file=sys.stderr)
        print(f"- URL: {url}", file=sys.stderr)
        if 'params' in kwargs:
            print(f"- Params: {kwargs['params']}", file=sys.stderr)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            print("\nResponse received:", file=sys.stderr)
            print(f"- Status: {response.status_code}", file=sys.stderr)
            
            if response.status_code == 401:
                print("✗ Authentication failed", file=sys.stderr)
                raise AuthenticationError("Invalid API key or authentication failed")
            elif response.status_code == 422:
                print("✗ Validation error", file=sys.stderr)
                raise ValidationError(f"Validation error: {response.text}")
            
            # For 500 errors, check if it's a task not found error
            if response.status_code == 500:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', '')
                    if 'not found' in error_msg.lower():
                        print(f"✗ Task not found: {error_msg}", file=sys.stderr)
                        raise TaskNotFoundError(error_msg)
                except (ValueError, AttributeError):
                    pass  # If we can't parse the error, treat as generic 500
                
            # Handle other errors
            if response.status_code >= 400:
                print(f"✗ API error {response.status_code}", file=sys.stderr)
                raise AparaviError(f"API error {response.status_code}: {response.text}")
            
            response_data = response.json()
            print("✓ Request successful", file=sys.stderr)
            return response_data
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Request failed: {str(e)}", file=sys.stderr)
            raise AparaviError(f"Request failed: {str(e)}")
    
    def validate_pipe(self, pipeline: Dict[str, Any]) -> ResultBase:
        """
        Validate a processing pipeline configuration
        
        Args:
            pipeline: The pipeline configuration to validate
            
        Returns:
            ResultBase: Response indicating success or failure
            
        Raises:
            ValidationError: If pipeline validation fails
            AuthenticationError: If authentication fails
            AparaviError: For other API errors
        """
        print("\nValidating pipeline configuration...", file=sys.stderr)
        
        response = self._make_request(
            method='POST',
            endpoint='/pipe/validate',
            json=pipeline
        )
        
        result = ResultBase(
            status=response['status'],
            data=response.get('data'),
            error=response.get('error'),
            metrics=response.get('metrics')
        )
        
        if result.status == 'Error':
            print(f"✗ Pipeline validation failed: {result.error}", file=sys.stderr)
            raise PipelineError(f"Pipeline validation failed: {result.error}")
        
        print("✓ Pipeline validation successful", file=sys.stderr)
        return result
    
    def get_task_status(self, token: str, task_type: str) -> ResultBase:
        """
        Get the status of a task
        
        Args:
            token: The task token received from start_task
            task_type: Type of processing as returned by the server
            
        Returns:
            ResultBase: Response containing task status
            
        Raises:
            TaskNotFoundError: If task is not found
            AuthenticationError: If authentication fails
            AparaviError: For other API errors
        """
        print(f"\nChecking status for task {token}...", file=sys.stderr)
        
        response = self._make_request(
            method='GET',
            endpoint='/task',
            params={'token': token, 'type': task_type}
        )
        
        result = ResultBase(
            status=response['status'],
            data=response.get('data'),
            error=response.get('error'),
            metrics=response.get('metrics')
        )
        
        if result.status == 'Error':
            if 'not found' in str(result.error).lower():
                print(f"✗ Task not found: {result.error}", file=sys.stderr)
                raise TaskNotFoundError(f"Task not found: {result.error}")
            print(f"✗ Failed to get task status: {result.error}", file=sys.stderr)
            raise AparaviError(f"Failed to get task status: {result.error}")
        
        print(f"✓ Task status retrieved successfully: {result.status}", file=sys.stderr)
        return result
    
    def end_task(self, token: str, task_type: str) -> ResultBase:
        """
        Cancel/end a task
        
        Args:
            token: The task token received from start_task
            task_type: Type of processing as returned by the server
            
        Returns:
            ResultBase: Response indicating success or failure
            
        Raises:
            TaskNotFoundError: If task is not found
            AuthenticationError: If authentication fails
            AparaviError: For other API errors
        """
        print(f"\nEnding task {token}...", file=sys.stderr)
        
        response = self._make_request(
            method='DELETE',
            endpoint='/task',
            params={'token': token, 'type': task_type}
        )
        
        result = ResultBase(
            status=response['status'],
            data=response.get('data'),
            error=response.get('error'),
            metrics=response.get('metrics')
        )
        
        if result.status == 'Error':
            if 'not found' in str(result.error).lower():
                print(f"✗ Task not found: {result.error}", file=sys.stderr)
                raise TaskNotFoundError(f"Task not found: {result.error}")
            print(f"✗ Failed to end task: {result.error}", file=sys.stderr)
            raise AparaviError(f"Failed to end task: {result.error}")
        
        print("✓ Task ended successfully", file=sys.stderr)
        return result 


