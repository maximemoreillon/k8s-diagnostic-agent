# K8s Diagnostic Agent — Specification

## Purpose

A conversational agent that diagnoses Kubernetes cluster issues in natural language. The user describes a problem or asks a question; the agent investigates the cluster autonomously using a set of read-only tools and returns a human-readable explanation.

---

## Tech Stack

| Component | Choice |
|-----------|--------|
| Language | Python |
| Agent framework | LangChain (ReAct) |
| LLM | Claude or OpenAI (configurable via env var) |
| K8s client | `kubernetes` Python client |
| Chat UI | Chainlit |
| Deployment | In-cluster Pod with ServiceAccount |

---

## Architecture

```
User (Chainlit UI)
      ↓
  ReAct Agent (LangChain)
      ↓ ↑ (tool calls + results)
  Tool Layer (kubernetes Python client)
      ↓
  K8s API Server
```

The agent runs a ReAct loop: reason → call tool → observe result → reason again → repeat until it has enough information to answer.

---

## Tools

| Tool | Inputs | Purpose |
|------|--------|---------|
| `list_namespaces` | — | Discover available namespaces |
| `list_pods` | `namespace` | Pod names, status, restart count, age |
| `describe_pod` | `name, namespace` | Conditions, events, resource limits, image |
| `get_pod_logs` | `name, namespace, tail=100, container=None` | Recent stdout/stderr |
| `list_deployments` | `namespace` | Ready vs desired replicas, conditions |
| `describe_deployment` | `name, namespace` | Strategy, conditions, events |
| `list_events` | `namespace, warnings_only=True` | Cluster events filtered to warnings |
| `get_node_status` | — | Node conditions, pressure flags, allocatable resources |
| `list_services` | `namespace` | Service names, types, selectors |

All tools return trimmed, structured text — not raw YAML. Only fields relevant to diagnosis are included to stay within context limits.

---

## Context Management

- Log tool capped at 100 lines by default; user can ask for more
- Describe tools return key fields only (not full object spec)
- Events filtered to `Warning` type by default
- Conversation history capped at last 10 turns

---

## System Prompt (outline)

- You are a Kubernetes diagnostic assistant
- You have read-only access to the cluster via a set of tools
- Always start by identifying the relevant namespace and resource before diving into logs
- When diagnosing, check events before logs — events are faster and often sufficient
- Common patterns to recognize: `CrashLoopBackOff`, `ImagePullBackOff`, `OOMKilled`, `Pending` due to insufficient resources or unschedulable nodes, failed readiness/liveness probes

---

## Deployment

**ServiceAccount + ClusterRole**: read-only access to pods, deployments, services, events, nodes, namespaces.

**Pod**: single container, mounts the ServiceAccount token automatically (standard in-cluster auth). Chainlit exposed via a K8s Service.

**Configuration via environment variables**: LLM provider, API key, model name.

---

## Out of Scope (v1)

- Write operations (no restarts, deletions, scaling)
- Prometheus / Loki integration (natural v2 extension)
- Multi-cluster support
- Authentication on the Chainlit UI

---

## Extension Path (v2)

Add Prometheus and Loki tools — `query_metrics(promql)` and `query_logs(logql, service, time_range)` — to answer latency and error-rate questions alongside structural K8s issues.
