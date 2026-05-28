# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A conversational Kubernetes diagnostic agent. The user describes a problem; the agent investigates the cluster autonomously using read-only tools and returns a human-readable explanation. See `k8s-diagnostic-agent-spec.md` for the full specification.

## Commands

```bash
# Set up virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the agent (once Chainlit is wired up)
chainlit run main.py

# Run directly (current skeleton)
python main.py
```

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

The agent runs a LangChain ReAct loop: reason → call tool → observe → repeat until it can answer. All Kubernetes tools are **read-only** and return trimmed structured text (not raw YAML) to stay within context limits.

## Tools to Implement

| Tool | Inputs |
|------|--------|
| `list_namespaces` | — |
| `list_pods` | `namespace` |
| `describe_pod` | `name, namespace` |
| `get_pod_logs` | `name, namespace, tail=100, container=None` |
| `list_deployments` | `namespace` |
| `describe_deployment` | `name, namespace` |
| `list_events` | `namespace, warnings_only=True` |
| `get_node_status` | — |
| `list_services` | `namespace` |

## Key Design Constraints

- **Read-only**: no write operations (no restarts, deletions, scaling)
- **Context management**: log tool capped at 100 lines, describe tools return key fields only, events filtered to `Warning` type by default, conversation history capped at 10 turns
- **LLM**: configurable via env vars (`LLM_PROVIDER`, `API_KEY`, `MODEL_NAME`) — supports Claude or OpenAI
- **Auth**: in-cluster uses ServiceAccount token automatically; local dev uses `~/.kube/config`

## Deployment

Runs as a Pod with a ServiceAccount bound to a ClusterRole granting read-only access to pods, deployments, services, events, nodes, and namespaces. Chainlit UI exposed via a Kubernetes Service.

## System Prompt Behavior

The agent should: check events before logs (faster, often sufficient), identify namespace and resource before diving into logs, and recognize common patterns: `CrashLoopBackOff`, `ImagePullBackOff`, `OOMKilled`, `Pending` (resource pressure or unschedulable nodes), failed readiness/liveness probes.
