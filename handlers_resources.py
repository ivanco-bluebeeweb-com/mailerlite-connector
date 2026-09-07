"""Resource handlers for MailerLite Connector."""
from __future__ import annotations
from typing import Any
from imperal_sdk import ActionResult
from app import chat
from schemas import (
    ListSubscriberParams, GetSubscriberParams,
    SubscriberRecord, SubscriberList, AuditHealthReport, ConnectionIdParams
)
from handlers_connection import resolve_client

@chat.function("list_subscribers", "List subscribers in MailerLite.", action_type="read", chain_callable=True, event="mailerlite-connector.list_subscribers", effects=["read:subscribers"], data_model=SubscriberList)
async def list_subscribers(params: ListSubscriberParams, ctx) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    try:
        raw_items = await client.list_subscribers(limit=params.limit)
        items = []
        for r in raw_items:
            rid = str(r.get("id") or r.get("key") or r.get("uuid") or "unknown")
            rname = r.get("name") or r.get("title") or r.get("label") or rid
            items.append({"id": rid, "name": rname, "status": r.get("status"), "created_at": r.get("createdAt") or r.get("created_at"), "raw": r})
        return ActionResult.success({"subscribers": items, "total": len(items)}, summary=f"Found {len(items)} subscribers.")
    except Exception as e:
        return ActionResult.error(f"Error listing subscribers: {e}")

@chat.function("get_subscriber", "Get details of one Subscriber in MailerLite.", action_type="read", chain_callable=True, event="mailerlite-connector.get_subscriber", effects=["read:subscriber"], data_model=SubscriberRecord)
async def get_subscriber(params: GetSubscriberParams, ctx) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    try:
        r = await client.get_subscriber(params.subscriber_id)
        rid = str(r.get("id") or params.subscriber_id)
        rname = r.get("name") or r.get("title") or rid
        return ActionResult.success({"id": rid, "name": rname, "status": r.get("status"), "created_at": r.get("createdAt") or r.get("created_at"), "raw": r}, summary=f"Retrieved Subscriber {rid}.")
    except Exception as e:
        return ActionResult.error(f"Error retrieving Subscriber: {e}")

@chat.function("audit_subscriber_health", "Audit health of MailerLite subscribers and connectivity.", action_type="read", chain_callable=True, event="mailerlite-connector.audit_subscriber_health", effects=["read:audit"], data_model=AuditHealthReport)
async def audit_subscriber_health(params: ConnectionIdParams, ctx) -> ActionResult:
    client = await resolve_client(ctx, params.connection_id)
    try:
        items = await client.list_subscribers(limit=50)
        return ActionResult.success({
            "healthy": True,
            "total_subscribers": len(items),
            "details": {"sample_count": len(items)},
            "summary": f"MailerLite healthy. Sampled {len(items)} subscribers."
        }, summary=f"MailerLite health check passed with {len(items)} subscribers.")
    except Exception as e:
        return ActionResult.error(f"Error auditing MailerLite health: {e}")
