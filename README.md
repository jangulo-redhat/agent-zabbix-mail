# Agent Demo: N8N + OpenShift AI

## Architecture

```
User ──► N8N Chat Trigger (webhook)
              │
              ▼
         N8N workflow
              │
         AI Agent (N8N)
         │    │    │
         ▼    ▼    ▼
       vLLM  Zabbix  Email
      (RHOAI)  MCP    MCP
                │
             Zabbix
```

| Component | Chart | Namespace |
|-----------|-------|-----------|
| Zabbix | zabbix-community/zabbix | zabbix |
| N8N | 8gears/n8n | n8n |
| Zabbix MCP | ./helm/zabbix-mcp | zabbix-mcp |
| Email MCP | ./helm/email-mcp | email-mcp |

## Deploy

### 0. Helm repos

```bash
helm repo add 8gears https://8gears.container-registry.com/chartrepo/library
helm repo add zabbix-community https://zabbix-community.github.io/helm-zabbix
helm repo update
```

### 1. Zabbix

```bash
oc new-project zabbix
helm upgrade --install zabbix zabbix-community/zabbix -f helm/zabbix/values.yaml -n zabbix
```

After install: **Administration → API tokens** → create token → copy for Zabbix MCP config.

### 2. N8N

Edit `helm/n8n/values.yaml`: set `encryptionKey` and `CLUSTER_DOMAIN`.

```bash
oc new-project n8n
helm upgrade --install n8n 8gears/n8n -f helm/n8n/values.yaml -n n8n
```

### 3. Build MCP images

```bash
podman build -t <REGISTRY>/zabbix-mcp:latest mcp-servers/zabbix/
podman build -t <REGISTRY>/email-mcp:latest  mcp-servers/email/
podman push <REGISTRY>/zabbix-mcp:latest
podman push <REGISTRY>/email-mcp:latest
```

### 4. Zabbix MCP

Edit `helm/zabbix-mcp/values.yaml`: set image, `zabbix.token`, and `route.host`.

```bash
oc new-project zabbix-mcp
helm upgrade --install zabbix-mcp ./helm/zabbix-mcp -n zabbix-mcp
```

### 5. Email MCP

Edit `helm/email-mcp/values.yaml`: set image, SMTP credentials, and `route.host`.

```bash
oc new-project email-mcp
helm upgrade --install email-mcp ./helm/email-mcp -n email-mcp
```

### 6. N8N Agent Workflow

In N8N UI (`https://n8n.apps.CLUSTER_DOMAIN`):

1. New Workflow → **Chat Trigger** node
2. **AI Agent** node:
   - Model: OpenAI Chat Model → Base URL: `https://<vllm-route>/v1`, API Key: `token` (or vLLM token), Model: deployed model name
3. **MCP Client Tool** node → URL: `http://zabbix-mcp.zabbix-mcp.svc.cluster.local:8080/mcp`
4. **MCP Client Tool** node → URL: `http://email-mcp.email-mcp.svc.cluster.local:8080/mcp`
5. Connect tools to AI Agent → Activate
6. Use the **Chat Trigger** production URL (or test URL) as the webhook endpoint for your chat client or integrations.

## MCP Tools Reference

**Zabbix MCP** (`/mcp`):
- `get_problems(min_severity)` — active alerts
- `get_hosts()` — monitored hosts
- `get_host_metrics(host)` — latest values for a host

**Email MCP** (`/mcp`):
- `send_email(to, subject, body)` — send via SMTP
