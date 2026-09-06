"""Official MailerLite REST API client aligned with connect.mailerlite.com/api."""
from __future__ import annotations
import httpx
from typing import Any, Optional

DEFAULT_MAILERLITE_BASE = "https://connect.mailerlite.com/api"

class MailerLiteClient:
    def __init__(self, api_key: str, base_url: str = ""):
        self.api_key = api_key.strip()
        self.base_url = (base_url.strip() if base_url else DEFAULT_MAILERLITE_BASE).rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Imperal-MailerLite/0.1.0"
        }
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    def _sanitize_msg(self, msg: str) -> str:
        if not msg:
            return ""
        if self.api_key and len(self.api_key) > 6:
            msg = msg.replace(self.api_key, self.api_key[:3] + "..." + self.api_key[-3:])
        return msg

    def _classify_error(self, resp: httpx.Response, action_name: str) -> dict[str, Any]:
        status = resp.status_code
        err_msg = ""
        try:
            data = resp.json()
            if "errors" in data and isinstance(data["errors"], dict):
                err_msg = "; ".join(f"{k}: {', '.join(v) if isinstance(v, list) else str(v)}" for k, v in data["errors"].items())
            elif "message" in data:
                err_msg = data["message"]
            elif "error" in data:
                err_msg = str(data["error"])
        except Exception:
            err_msg = resp.text[:200]
        err_msg = self._sanitize_msg(err_msg)

        if status == 429:
            retry_after = resp.headers.get("Retry-After", "60")
            return {
                "status": "error",
                "code": "RATE_LIMITED",
                "message": f"MailerLite rate limit exceeded on {action_name}. Retry after {retry_after}s. Details: {err_msg}",
                "retry_after": int(retry_after) if retry_after.isdigit() else 60
            }
        elif status == 401:
            return {
                "status": "error",
                "code": "UNAUTHORIZED",
                "message": f"MailerLite authentication failed on {action_name}. API key invalid or expired."
            }
        elif status == 403:
            return {
                "status": "error",
                "code": "FORBIDDEN",
                "message": f"Access forbidden for MailerLite operation {action_name}. Check API key scopes."
            }
        elif status == 404:
            return {
                "status": "error",
                "code": "NOT_FOUND",
                "message": f"MailerLite resource not found on {action_name}: {err_msg}"
            }
        return {
            "status": "error",
            "code": f"HTTP_{status}",
            "message": f"MailerLite {action_name} failed with HTTP {status}: {err_msg}"
        }

    async def ping(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/subscribers?limit=1", headers=self.headers)
                if resp.status_code == 200:
                    return {"status": "ok", "authenticated": True}
                return self._classify_error(resp, "ping")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def list_subscribers(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        params: dict[str, Any] = {"limit": min(limit, 100)}
        if cursor:
            params["cursor"] = cursor
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/subscribers", headers=self.headers, params=params)
                if resp.status_code == 200:
                    body = resp.json()
                    data = body.get("data", [])
                    meta = body.get("meta", {})
                    return {"items": data, "total": meta.get("total", len(data)), "next_cursor": meta.get("next_cursor")}
                return self._classify_error(resp, "list_subscribers")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def get_subscriber(self, subscriber_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/subscribers/{subscriber_id}", headers=self.headers)
                if resp.status_code == 200:
                    return resp.json().get("data", {})
                return self._classify_error(resp, "get_subscriber")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def create_subscriber(self, email: str, fields: Optional[dict[str, Any]] = None, groups: Optional[list[str]] = None, status: str = "active") -> dict[str, Any]:
        payload: dict[str, Any] = {"email": email, "status": status}
        if fields: payload["fields"] = fields
        if groups: payload["groups"] = groups
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(f"{self.base_url}/subscribers", headers=self.headers, json=payload)
                if resp.status_code in (200, 201):
                    return resp.json().get("data", {})
                return self._classify_error(resp, "create_subscriber")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def update_subscriber(self, subscriber_id: str, fields: Optional[dict[str, Any]] = None, status: Optional[str] = None) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if fields: payload["fields"] = fields
        if status: payload["status"] = status
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.put(f"{self.base_url}/subscribers/{subscriber_id}", headers=self.headers, json=payload)
                if resp.status_code == 200:
                    return resp.json().get("data", {})
                return self._classify_error(resp, "update_subscriber")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def delete_subscriber(self, subscriber_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.delete(f"{self.base_url}/subscribers/{subscriber_id}", headers=self.headers)
                if resp.status_code in (200, 204):
                    return {"status": "deleted", "id": subscriber_id}
                return self._classify_error(resp, "delete_subscriber")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def list_campaigns(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        params: dict[str, Any] = {"limit": min(limit, 100)}
        if cursor: params["cursor"] = cursor
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/campaigns", headers=self.headers, params=params)
                if resp.status_code == 200:
                    body = resp.json()
                    data = body.get("data", [])
                    return {"items": data, "total": len(data)}
                return self._classify_error(resp, "list_campaigns")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def get_campaign(self, campaign_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/campaigns/{campaign_id}", headers=self.headers)
                if resp.status_code == 200:
                    return resp.json().get("data", {})
                return self._classify_error(resp, "get_campaign")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def create_campaign(self, name: str, subject: str = "", groups: Optional[list[str]] = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"name": name, "type": "regular"}
        if subject: payload["emails"] = [{"subject": subject, "from_name": "Team"}]
        if groups: payload["groups"] = groups
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(f"{self.base_url}/campaigns", headers=self.headers, json=payload)
                if resp.status_code in (200, 201):
                    return resp.json().get("data", {})
                return self._classify_error(resp, "create_campaign")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def delete_campaign(self, campaign_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.delete(f"{self.base_url}/campaigns/{campaign_id}", headers=self.headers)
                if resp.status_code in (200, 204):
                    return {"status": "deleted", "id": campaign_id}
                return self._classify_error(resp, "delete_campaign")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def list_groups(self, limit: int = 50) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/groups", headers=self.headers, params={"limit": limit})
                if resp.status_code == 200:
                    body = resp.json()
                    return {"items": body.get("data", [])}
                return self._classify_error(resp, "list_groups")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def list_segments(self, limit: int = 50) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/segments", headers=self.headers, params={"limit": limit})
                if resp.status_code == 200:
                    body = resp.json()
                    return {"items": body.get("data", [])}
                return self._classify_error(resp, "list_segments")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def list_automations(self, limit: int = 50) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/automations", headers=self.headers, params={"limit": limit})
                if resp.status_code == 200:
                    body = resp.json()
                    return {"items": body.get("data", [])}
                return self._classify_error(resp, "list_automations")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def list_templates(self, limit: int = 50) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/templates", headers=self.headers, params={"limit": limit})
                if resp.status_code == 200:
                    body = resp.json()
                    return {"items": body.get("data", [])}
                return self._classify_error(resp, "list_templates")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}
