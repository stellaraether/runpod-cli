"""RunPod API client for serverless endpoints."""

from typing import Optional

import requests


class RunPodClient:
    """Client for RunPod serverless API endpoints."""

    BASE_URL = "https://api.runpod.ai/v2"

    def __init__(self, api_key: str, timeout: int = 300):
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )

    def run_sync(self, endpoint_id: str, input_data: dict) -> dict:
        """Run a job synchronously and wait for completion.

        Args:
            endpoint_id: The RunPod endpoint ID.
            input_data: The input payload for the endpoint.

        Returns:
            The JSON response from the endpoint.
        """
        url = f"{self.BASE_URL}/{endpoint_id}/runsync"
        response = self.session.post(url, json={"input": input_data}, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def run_async(self, endpoint_id: str, input_data: dict) -> dict:
        """Run a job asynchronously and return the job ID.

        Args:
            endpoint_id: The RunPod endpoint ID.
            input_data: The input payload for the endpoint.

        Returns:
            The JSON response containing the job ID.
        """
        url = f"{self.BASE_URL}/{endpoint_id}/run"
        response = self.session.post(url, json={"input": input_data}, timeout=60)
        response.raise_for_status()
        return response.json()

    def get_status(self, endpoint_id: str, job_id: str) -> dict:
        """Get the status of an async job.

        Args:
            endpoint_id: The RunPod endpoint ID.
            job_id: The job ID returned by run_async.

        Returns:
            The JSON response with job status and output.
        """
        url = f"{self.BASE_URL}/{endpoint_id}/status/{job_id}"
        response = self.session.get(url, timeout=60)
        response.raise_for_status()
        return response.json()

    def cancel_job(self, endpoint_id: str, job_id: str) -> dict:
        """Cancel an async job.

        Args:
            endpoint_id: The RunPod endpoint ID.
            job_id: The job ID to cancel.

        Returns:
            The JSON response confirming cancellation.
        """
        url = f"{self.BASE_URL}/{endpoint_id}/cancel/{job_id}"
        response = self.session.post(url, timeout=60)
        response.raise_for_status()
        return response.json()
