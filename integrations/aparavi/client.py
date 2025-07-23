"""
Aparavi Client for MCP Server
"""

import time
import requests
from typing import Optional, Dict, Any, Literal, Tuple
from .models import ResultBase
from .exceptions import AparaviError, AuthenticationError, ValidationError, TaskNotFoundError, PipelineError, TaskTimeoutError


class AparaviClient:
    """
    Client for interacting with Aparavi Web Services API
    """
    
    def __init__(self, base_url: str = "https://eaas-dev.aparavi.com", api_key: str = None, timeout: int = 120):
        """
        Initialize the Aparavi client
        
        Args:
            base_url: The base URL of the Aparavi API
            api_key: The API key for authentication
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def wait_for_task_ready(
        self, 
        task_token: str, 
        type: Literal['gpu', 'cpu'] = 'cpu',
        max_retries: int = 5,
        initial_delay: float = 2.0,
        timeout: Optional[float] = None
    ) -> Tuple[bool, ResultBase]:
        """
        Wait for a task to be ready with exponential backoff
        
        Args:
            task_token: The task token to check
            type: Type of processing ('gpu' or 'cpu')
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
        delay = initial_delay
        start_time = time.time()
        last_status = None

        # Initial wait to let task initialize
        print(f"Waiting {delay} seconds for initial task setup...")
        time.sleep(delay)

        for attempt in range(max_retries):
            if timeout and (time.time() - start_time) > timeout:
                raise TaskTimeoutError(f"Task {task_token} failed to become ready within {timeout} seconds")

            print(f"\nChecking task status (attempt {attempt + 1}/{max_retries})...")
            
            try:
                result = self.get_task_status(task_token, type)
                last_status = result

                # Check if service is up and ready
                if result.data and result.data.get("serviceUp"):
                    return True, result

                # Not ready yet, wait before next attempt if not last attempt
                print(f"Service exists but not ready yet (serviceUp: {result.data.get('serviceUp', False)})")
                
            except TaskNotFoundError:
                print(f"Task not found (attempt {attempt + 1}/{max_retries})")
                result = None
                
            except Exception as e:
                # For any other errors, stop retrying
                raise AparaviError(f"Error checking task status: {str(e)}")

            # If we get here and it's the last attempt, raise appropriate error
            if attempt == max_retries - 1:
                if result is None:
                    raise TaskNotFoundError(f"Task {task_token} not found after {max_retries} attempts")
                return False, last_status

            # Not the last attempt, wait and continue
            delay += 2  # Double the delay for next attempt
            print(f"Waiting {delay} seconds before next check...")
            time.sleep(delay)

        return False, last_status

    def create_and_wait_for_task(
        self,
        pipeline: Dict[str, Any],
        name: Optional[str] = None,
        threads: Optional[int] = None,
        type: Literal['gpu', 'cpu'] = 'cpu',
        max_retries: int = 5,
        initial_delay: float = 2.0,
        timeout: Optional[float] = None
    ) -> Tuple[str, ResultBase]:
        """
        Create a task and wait for it to be ready
        
        Args:
            pipeline: The pipeline configuration
            name: Optional name for the task
            threads: Optional number of threads (1-16)
            type: Type of processing ('gpu' or 'cpu')
            max_retries: Maximum number of retries for status check
            initial_delay: Initial delay for status check
            timeout: Maximum total time to wait
            
        Returns:
            Tuple[str, ResultBase]: (task_token, ready_status)
            
        Raises:
            ValidationError: If pipeline validation fails
            TaskTimeoutError: If task fails to become ready
            AparaviError: For other API errors
        """
        # First validate the pipeline
        self.validate_pipe(pipeline)
        
        # Create the task
        result = self.start_task(pipeline, name, threads, type)
        task_token = result.data["token"]
        
        print(f"Task created with token: {task_token}")
        print("Waiting for service to be ready...")
        
        # Wait for task to be ready
        is_ready, status = self.wait_for_task_ready(
            task_token=task_token,
            type=type,
            max_retries=max_retries,
            initial_delay=initial_delay,
            timeout=timeout
        )
        
        if not is_ready:
            raise TaskTimeoutError(f"Task {task_token} failed to become ready after {max_retries} attempts")
            
        return task_token, status
    
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
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key or authentication failed")
            elif response.status_code == 422:
                raise ValidationError(f"Validation error: {response.text}")
            
            # For 500 errors, check if it's a task not found error
            if response.status_code == 500:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', '')
                    if 'not found' in error_msg.lower():
                        raise TaskNotFoundError(error_msg)
                except (ValueError, AttributeError):
                    pass  # If we can't parse the error, treat as generic 500
                
            # Handle other errors
            if response.status_code >= 400:
                raise AparaviError(f"API error {response.status_code}: {response.text}")
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
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
            raise PipelineError(f"Pipeline validation failed: {result.error}")
        
        return result
    
    def start_task(self, pipeline: Dict[str, Any], name: Optional[str] = None, 
                   threads: Optional[int] = None, type: Literal['gpu', 'cpu'] = 'cpu') -> ResultBase:
        """
        Execute a task with the given pipeline configuration
        
        Args:
            pipeline: The pipeline configuration
            name: Optional name for the task
            threads: Optional number of threads to use (1-16)
            type: Type of processing to use ('gpu' or 'cpu')
            
        Returns:
            ResultBase: Response containing task token on success
            
        Raises:
            ValidationError: If pipeline validation fails
            AuthenticationError: If authentication fails
            AparaviError: For other API errors
        """
        params = {'type': type}
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
            raise AparaviError(f"Task execution failed: {result.error}")
        
        return result
    
    def get_task_status(self, token: str, type: Literal['gpu', 'cpu'] = 'cpu') -> ResultBase:
        """
        Get the status of a task
        
        Args:
            token: The task token received from start_task
            type: Type of processing to check ('gpu' or 'cpu')
            
        Returns:
            ResultBase: Response containing task status
            
        Raises:
            TaskNotFoundError: If task is not found
            AuthenticationError: If authentication fails
            AparaviError: For other API errors
        """
        response = self._make_request(
            method='GET',
            endpoint='/task',
            params={'token': token, 'type': type}
        )
        
        result = ResultBase(
            status=response['status'],
            data=response.get('data'),
            error=response.get('error'),
            metrics=response.get('metrics')
        )
        
        if result.status == 'Error':
            if 'not found' in str(result.error).lower():
                raise TaskNotFoundError(f"Task not found: {result.error}")
            raise AparaviError(f"Failed to get task status: {result.error}")
        
        return result
    
    def end_task(self, token: str) -> ResultBase:
        """
        Cancel/end a task
        
        Args:
            token: The task token received from start_task
            
        Returns:
            ResultBase: Response indicating success or failure
            
        Raises:
            TaskNotFoundError: If task is not found
            AuthenticationError: If authentication fails
            AparaviError: For other API errors
        """
        response = self._make_request(
            method='DELETE',
            endpoint='/task',
            params={'token': token}
        )
        
        result = ResultBase(
            status=response['status'],
            data=response.get('data'),
            error=response.get('error'),
            metrics=response.get('metrics')
        )
        
        if result.status == 'Error':
            if 'not found' in str(result.error).lower():
                raise TaskNotFoundError(f"Task not found: {result.error}")
            raise AparaviError(f"Failed to end task: {result.error}")
        
        return result

    def post_to_webhook(self, token: str, data: Optional[Dict[str, Any]] = None, type: Literal['gpu', 'cpu'] = 'cpu') -> Dict[str, Any]:
        """
        Send a webhook request to the task engine
        
        Args:
            token: The task token
            data: Optional data to send in the webhook request
            type: Type of processing to use ('gpu' or 'cpu')
            
        Returns:
            Dict: Response from the webhook endpoint
            
        Raises:
            TaskNotFoundError: If task is not found
            AuthenticationError: If authentication fails
            AparaviError: For other API errors
        """
        kwargs = {'params': {'token': token, 'type': type}}
        if data:
            kwargs['json'] = data
        
        response = self._make_request(
            method='PUT',
            endpoint='/webhook',
            **kwargs
        )
        
        return response 


