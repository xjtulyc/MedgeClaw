#!/usr/bin/env python3
"""
Feishu Rich Card Sender — 飞书图文混排卡片发送工具

Usage:
    from send_card import FeishuCardSender
    sender = FeishuCardSender()
    sender.send_rich_card(chat_id, title, elements)

Or standalone:
    python3 send_card.py --chat oc_xxx --title "Report" --image /tmp/plot.png --text "Done!"
"""

import json
import os
import sys
import requests
from pathlib import Path
from typing import Optional

# ─── Config ──────────────────────────────────────────────────────────────

OPENCLAW_CONFIG = Path.home() / ".openclaw" / "openclaw.json"
DEFAULT_CHAT_ID = os.environ.get("FEISHU_DEFAULT_CHAT_ID", "")

# ─── Token Cache ─────────────────────────────────────────────────────────

_token_cache: dict = {}


def _get_credentials() -> dict:
    """Read Feishu appId/appSecret from openclaw.json."""
    with open(OPENCLAW_CONFIG) as f:
        cfg = json.load(f)
    feishu = cfg.get("channels", {}).get("feishu", {})
    # Check accounts first, then top-level
    accounts = feishu.get("accounts", {})
    if accounts:
        first = next(iter(accounts.values()))
        return {
            "app_id": first.get("appId", feishu.get("appId")),
            "app_secret": first.get("appSecret", feishu.get("appSecret")),
            "domain": first.get("domain", feishu.get("domain", "feishu")),
        }
    return {
        "app_id": feishu.get("appId"),
        "app_secret": feishu.get("appSecret"),
        "domain": feishu.get("domain", "feishu"),
    }


def _api_base(domain: str = "feishu") -> str:
    if domain == "lark":
        return "https://open.larksuite.com/open-apis"
    return "https://open.feishu.cn/open-apis"


def _get_token(creds: dict) -> str:
    """Get or refresh tenant access token."""
    import time

    cache_key = creds["app_id"]
    cached = _token_cache.get(cache_key)
    if cached and cached["expires_at"] > time.time() + 60:
        return cached["token"]

    base = _api_base(creds.get("domain", "feishu"))
    resp = requests.post(
        f"{base}/auth/v3/tenant_access_token/internal",
        json={"app_id": creds["app_id"], "app_secret": creds["app_secret"]},
    )
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"Token error: {data.get('msg')}")

    token = data["tenant_access_token"]
    _token_cache[cache_key] = {
        "token": token,
        "expires_at": time.time() + data.get("expire", 7200),
    }
    return token


# ─── Core Functions ──────────────────────────────────────────────────────


class FeishuCardSender:
    def __init__(self, creds: Optional[dict] = None):
        self.creds = creds or _get_credentials()
        self.base = _api_base(self.creds.get("domain", "feishu"))

    @property
    def token(self) -> str:
        return _get_token(self.creds)

    def upload_image(self, image_path: str) -> str:
        """Upload a local image file and return image_key."""
        with open(image_path, "rb") as f:
            resp = requests.post(
                f"{self.base}/im/v1/images",
                headers={"Authorization": f"Bearer {self.token}"},
                data={"image_type": "message"},
                files={"image": (Path(image_path).name, f, "image/png")},
            )
        data = resp.json()
        if data.get("code") != 0:
            raise RuntimeError(f"Image upload failed: {data.get('msg')}")
        return data["data"]["image_key"]

    def send_rich_card(
        self,
        chat_id: str,
        title: str,
        elements: list[dict],
        header_template: str = "blue",
        reply_to: Optional[str] = None,
    ) -> dict:
        """
        Send a rich card with mixed text and images.

        elements: list of dicts, each with:
          - {"type": "markdown", "content": "**bold** text"}
          - {"type": "image", "path": "/tmp/img.png", "alt": "description"}
          - {"type": "image_key", "key": "img_v3_xxx", "alt": "description"}
          - {"type": "hr"}
          - {"type": "note", "content": "footer text"}
          - {"type": "column_set", "columns": [...]}  # advanced
        """
        card_elements = []
        for elem in elements:
            t = elem.get("type", "")
            if t == "markdown":
                card_elements.append({"tag": "markdown", "content": elem["content"]})
            elif t == "image":
                image_key = self.upload_image(elem["path"])
                card_elements.append(
                    {
                        "tag": "img",
                        "img_key": image_key,
                        "alt": {"tag": "plain_text", "content": elem.get("alt", "")},
                    }
                )
            elif t == "image_key":
                card_elements.append(
                    {
                        "tag": "img",
                        "img_key": elem["key"],
                        "alt": {"tag": "plain_text", "content": elem.get("alt", "")},
                    }
                )
            elif t == "hr":
                card_elements.append({"tag": "hr"})
            elif t == "note":
                card_elements.append(
                    {
                        "tag": "note",
                        "elements": [
                            {"tag": "plain_text", "content": elem["content"]}
                        ],
                    }
                )
            else:
                print(f"Warning: unknown element type '{t}', skipping", file=sys.stderr)

        card = {
            "schema": "2.0",
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": header_template,
            },
            "body": {"elements": card_elements},
        }

        payload = {
            "receive_id": chat_id,
            "msg_type": "interactive",
            "content": json.dumps(card, ensure_ascii=False),
        }

        if reply_to:
            resp = requests.post(
                f"{self.base}/im/v1/messages/{reply_to}/reply",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
                json={"msg_type": "interactive", "content": json.dumps(card, ensure_ascii=False)},
            )
        else:
            resp = requests.post(
                f"{self.base}/im/v1/messages",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
                params={"receive_id_type": "chat_id"},
                json=payload,
            )

        data = resp.json()
        if data.get("code") != 0:
            raise RuntimeError(f"Send card failed: {data.get('msg')}")
        return data

    def send_image_report(
        self,
        chat_id: str,
        title: str,
        image_path: str,
        intro: str = "",
        conclusion: str = "",
        header_template: str = "blue",
    ) -> dict:
        """Quick helper: send a single-image report card."""
        elements = []
        if intro:
            elements.append({"type": "markdown", "content": intro})
        elements.append({"type": "image", "path": image_path, "alt": title})
        if conclusion:
            elements.append({"type": "markdown", "content": conclusion})
        return self.send_rich_card(chat_id, title, elements, header_template)

    def send_progress_report(
        self,
        chat_id: str,
        title: str,
        sections: list[dict],
        header_template: str = "indigo",
    ) -> dict:
        """
        Send a structured progress report.

        sections: list of dicts:
          - {"heading": "...", "body": "...", "image": "/path/to/img.png" (optional)}
        """
        elements = []
        for i, sec in enumerate(sections):
            if i > 0:
                elements.append({"type": "hr"})
            heading = sec.get("heading", "")
            body = sec.get("body", "")
            md = ""
            if heading:
                md += f"## {heading}\n\n"
            if body:
                md += body
            if md:
                elements.append({"type": "markdown", "content": md})
            if sec.get("image"):
                elements.append(
                    {"type": "image", "path": sec["image"], "alt": heading or "image"}
                )
        return self.send_rich_card(chat_id, title, elements, header_template)


# ─── CLI ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Send Feishu rich card")
    parser.add_argument("--chat", default=DEFAULT_CHAT_ID, help="Chat ID")
    parser.add_argument("--title", required=True, help="Card title")
    parser.add_argument("--image", action="append", help="Image path(s)")
    parser.add_argument("--text", action="append", help="Text section(s)")
    parser.add_argument("--template", default="blue", help="Header color template")
    args = parser.parse_args()

    sender = FeishuCardSender()
    elements = []
    texts = args.text or []
    images = args.image or []

    # Interleave text and images
    max_len = max(len(texts), len(images))
    for i in range(max_len):
        if i < len(texts):
            elements.append({"type": "markdown", "content": texts[i]})
        if i < len(images):
            elements.append({"type": "image", "path": images[i], "alt": f"Image {i+1}"})

    result = sender.send_rich_card(args.chat, args.title, elements, args.template)
    print(f"✅ Sent! message_id={result['data']['message_id']}")
