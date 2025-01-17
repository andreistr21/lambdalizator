from __future__ import annotations

import json


class Response:
    """Response from lambda.

    Performs automatic dumping when body is dict. Otherwise payload just passes through."""

    def __init__(
        self,
        body: str | dict,
        /,
        headers: dict | None = None,
        status_code: int = 200,
        base64_encoded: bool = False,
    ):
        self.body = body
        self.is_json = isinstance(body, dict)
        self.headers = headers if headers is not None else self.get_content_header()
        self.status_code = status_code
        self.is_base64 = base64_encoded

    def __repr__(self) -> str:
        return f"<Response(status_code={self.status_code})>"

    def get_content_header(self) -> dict:
        """Adds necessary headers based on content type"""
        if self.is_json:
            return {"Content-Type": "application/json"}
        if isinstance(self.body, str):
            return {"Content-Type": "text/plain"}
        raise RuntimeError("Response body type not supported yet.")

    def to_dict(self) -> dict:
        """Dumps response to AWS Lambda compatible response format."""
        body = (
            json.dumps(self.body, separators=(",", ":"), default=str)
            if self.is_json
            else self.body
        )
        response = {
            "headers": self.headers,
            "statusCode": self.status_code,
            "body": body,
            "isBase64Encoded": self.is_base64,
        }

        return response

    def is_ok(self) -> bool:
        return self.status_code < 400
