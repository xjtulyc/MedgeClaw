# Feishu (Lark) Setup for OpenClaw

This guide covers connecting MedgeClaw (via OpenClaw) to Feishu for messaging. Based on real deployment experience and common pitfalls.

## Prerequisites

- OpenClaw installed and running
- A Feishu organization (enterprise or personal)
- Access to [Feishu Open Platform](https://open.feishu.cn/)

## Step 1: Create a Feishu App

1. Go to https://open.feishu.cn/ → Developer Console
2. Create a new Custom App (自建应用)
3. Note the **App ID** and **App Secret**

## Step 2: Configure OpenClaw

Add to `~/.openclaw/openclaw.json`:

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "<your-app-id>",
      "appSecret": "<your-app-secret>",
      "domain": "feishu",
      "groupPolicy": "open"
    }
  }
}
```

## Step 3: Enable Bot Capability

In the Feishu Developer Console:
1. Go to your app → Features → Bot
2. Enable the bot capability

## Step 4: Permissions

**This is where most problems occur.** Feishu has two permission types:

| Type | Chinese | Used By |
|------|---------|---------|
| **Tenant** (应用身份) | 应用身份权限 | Bot actions (sending messages, reactions, cards) |
| **User** (用户身份) | 用户身份权限 | Actions on behalf of a user |

**The bot needs tenant-level permissions.** User-level permissions alone are not enough.

### Required Tenant Permissions

Messaging (minimum for bot to work):

| Scope | Purpose |
|-------|---------|
| `im:message` | Send and manage messages |
| `im:message:send_as_bot` | Send messages as bot |
| `im:message:readonly` | Read messages |
| `im:message.p2p_msg:readonly` | Read P2P messages |
| `im:message.group_at_msg:readonly` | Read group @mentions |
| `im:chat:readonly` | Read chat info |
| `im:resource` | Download files/images from messages |
| `im:message.reactions:write_only` | Add emoji reactions |
| `contact:user.base:readonly` | Read basic user info |
| `cardkit:card:write` | Send message cards (required for streaming replies) |

Optional but recommended:

| Scope | Purpose |
|-------|---------|
| `im:message.group_msg` | Send messages to groups |
| `im:message:update` | Edit sent messages |
| `im:message:recall` | Recall messages |

For document/wiki/bitable features:

| Scope | Purpose |
|-------|---------|
| `docx:document` | Read/write documents |
| `wiki:wiki` | Read/write wiki |
| `drive:drive` | Read/write drive |
| `bitable:app` | Read/write bitable |

### Common Mistake: Tenant vs User

If you see this error in logs:

```
Access denied. One of the following scopes is required: [im:message, im:message.reactions:write_only].
应用尚未开通所需的应用身份权限
```

It means you added the permission as **user** type but the bot needs it as **tenant** type. Go back to the permission page and check the "应用身份" column.

### Publishing Required

**Permission changes require publishing a new app version to take effect.** After adding permissions:
1. Go to App Release → Create Version
2. Submit for review (self-built apps in personal orgs are usually auto-approved)

## Step 5: Event Subscription

OpenClaw uses WebSocket mode for receiving events. In the Developer Console:

1. Go to Events and Callbacks (事件与回调)
2. Set subscription mode to **Persistent Connection** (长连接)
3. Add event: `im.message.receive_v1`

## Step 6: Verify

After configuration, restart the gateway:

```bash
openclaw gateway restart
```

Check logs for successful connection:

```bash
journalctl --user -u openclaw-gateway -f | grep feishu
```

You should see:
```
[feishu] starting feishu[default] (mode: websocket)
[feishu] feishu[default]: bot open_id resolved: ou_xxxxx
[info]: [ 'event-dispatch is ready' ]
[feishu] feishu[default]: WebSocket client started
[info]: [ '[ws]', 'ws client ready' ]
```

## Troubleshooting

### `cardkit:card:write` Error

```
streaming start failed: Create card failed: Access denied.
One of the following scopes is required: [cardkit:card:write]
```

Add `cardkit:card:write` as a **tenant** permission and publish a new version.

### Duplicate Plugin Warning

```
plugin feishu: duplicate plugin id detected
```

This happens when feishu plugin exists in both `~/.openclaw/extensions/feishu/` and the npm global package. Remove the local one:

```bash
rm -rf ~/.openclaw/extensions/feishu
openclaw gateway restart
```

### Bot Receives Messages but Doesn't Reply

Check these in order:

1. **Gateway token mismatch** — After restart, the agent session may lose connection. Refresh webchat or restart gateway again.
2. **Context window error** — Check logs for "Model context window too small". This means the session history is too large.
3. **Permission error** — Check logs for "Access denied" and add the missing tenant permission.

### Messages Dispatched but `replies=0`

The agent session received the message but produced no reply. Common causes:
- Agent is still bootstrapping (first message after restart)
- Model API error (check logs for HTTP errors)
- Session was aborted by a concurrent gateway restart
