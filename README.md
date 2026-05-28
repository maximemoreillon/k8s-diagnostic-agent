# K8s Diagnostic Agent

A conversational agent that diagnoses Kubernetes cluster issues in natural language. Describe a problem and the agent investigates the cluster autonomously using read-only tools, then returns a human-readable explanation.

## Features

- Inspect namespaces, pods, deployments, services, and nodes
- Fetch pod logs and events
- Identify common failure patterns: `CrashLoopBackOff`, `ImagePullBackOff`, `OOMKilled`, failed probes, resource pressure
- Conversational — ask follow-up questions in the same session

## Tech stack

- **Agent**: LangChain
- **LLM**: OpenAI (configurable)
- **UI**: Chainlit
- **K8s client**: `kubernetes` Python client

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
chainlit run main.py -w
```

Requires a `~/.kube/config` for local development. Copy `.env.example` to `.env` and fill in your API key.

## CI/CD

The image is built and pushed to Docker Hub automatically via GitHub Actions on push to `main`/`master`.

## Deployment

The application requires a `ServiceAccount` with a `ClusterRole` granting read-only access to pods, deployments, services, events, nodes, and namespaces, and an `OPENAI_API_KEY` environment variable injected via a secret.
