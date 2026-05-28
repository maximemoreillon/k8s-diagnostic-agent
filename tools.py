from langchain.tools import tool
from k8s import v1


@tool
def list_namespaces() -> str:
    """List namespaces"""
    ret = v1.list_namespace()
    return "\n".join(i.metadata.name for i in ret.items)


@tool
def list_pods(namespace: str) -> str:
    """List pods in the given namespace with their status and restart count"""
    ret = v1.list_namespaced_pod(namespace=namespace)

    return "\n".join(
        f"{i.metadata.name}  {i.status.phase}  restarts:{sum(cs.restart_count for cs in (i.status.container_statuses or []))}"
        for i in ret.items
    )
