from langchain.tools import tool
from k8s import v1
import json


@tool
def list_namespaces() -> str:
    """List namespaces"""
    ret = v1.list_namespace()
    return "\n".join(i.metadata.name for i in ret.items)


@tool
def list_pods(namespace: str) -> str:
    """List pods in the given namespace with their status, ready/not-ready count, and restart count"""
    ret = v1.list_namespaced_pod(namespace=namespace)

    return "\n".join(
        f"{i.metadata.name}  {i.status.phase}  {sum(cs.ready for cs in (i.status.container_statuses or []))}/{len(i.status.container_statuses or [])}  restarts:{sum(cs.restart_count for cs in (i.status.container_statuses or []))}"
        for i in ret.items
    )


@tool
def describe_pod(name: str, namespace: str) -> str:
    """Describes a pod"""
    ret = v1.read_namespaced_pod(name=name, namespace=namespace)

    conditions = [c.to_dict() for c in ret.status.conditions]

    containers = [
        {
            "image": ret.spec.containers[i].image,
            "state": ret.status.container_statuses[i].state.to_dict(),
            "limits": ret.spec.containers[i].resources.limits,
        }
        for i in range(len(ret.spec.containers))
    ]

    return json.dumps({"conditions": conditions, "containers": containers}, default=str)
