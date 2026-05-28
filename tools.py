from langchain.tools import tool
from k8s import core_v1, apps_v1
import json


@tool
def list_namespaces() -> str:
    """List namespaces"""
    ret = core_v1.list_namespace()
    return "\n".join(i.metadata.name for i in ret.items)


@tool
def list_pods(namespace: str) -> str:
    """List pods in the given namespace with their status, ready/not-ready count, and restart count"""
    ret = core_v1.list_namespaced_pod(namespace=namespace)

    return "\n".join(
        f"{i.metadata.name}  {i.status.phase}  {sum(cs.ready for cs in (i.status.container_statuses or []))}/{len(i.status.container_statuses or [])}  restarts:{sum(cs.restart_count for cs in (i.status.container_statuses or []))}"
        for i in ret.items
    )


@tool
def describe_pod(name: str, namespace: str) -> str:
    """Describes a pod"""
    ret = core_v1.read_namespaced_pod(name=name, namespace=namespace)

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


@tool
def get_pod_logs(name: str, namespace: str, tail: int = 100) -> str:
    """Get logs of a pod"""

    logs = core_v1.read_namespaced_pod_log(
        name=name, namespace=namespace, tail_lines=tail
    )

    return logs


@tool
def list_deployments(namespace: str) -> str:
    """List deployments in the given namespace with their ready/desired replica counts"""
    ret = apps_v1.list_namespaced_deployment(namespace=namespace)
    return "\n".join(
        f"{d.metadata.name}  {d.status.ready_replicas or 0}/{d.spec.replicas}"
        for d in ret.items
    )


@tool
def describe_deployment(name: str, namespace: str) -> str:
    """Describe a deployment including its strategy, conditions, and container images"""
    d = apps_v1.read_namespaced_deployment(name=name, namespace=namespace)
    return json.dumps(
        {
            "images": [c.image for c in d.spec.template.spec.containers],
            "replicas": {
                "desired": d.spec.replicas,
                "ready": d.status.ready_replicas or 0,
                "available": d.status.available_replicas or 0,
            },
            "strategy": d.spec.strategy.type,
            "conditions": [c.to_dict() for c in (d.status.conditions or [])],
        },
        default=str,
    )


@tool
def list_events(namespace: str, warnings_only: bool = True) -> str:
    """List events in the given namespace, filtered to warnings by default"""
    ret = core_v1.list_namespaced_event(namespace=namespace)
    events = [e for e in ret.items if not warnings_only or e.type == "Warning"]
    return "\n".join(
        f"{e.last_timestamp}  {e.involved_object.kind}/{e.involved_object.name}  {e.reason}  {e.message}"
        for e in events
    )


@tool
def get_node_status() -> str:
    """Get status of all nodes including conditions and allocatable resources"""
    ret = core_v1.list_node()
    nodes = []
    for n in ret.items:
        conditions = {c.type: c.status for c in (n.status.conditions or [])}
        nodes.append(
            {
                "name": n.metadata.name,
                "conditions": conditions,
                "allocatable": n.status.allocatable,
            }
        )
    return json.dumps(nodes, default=str)


@tool
def list_services(namespace: str) -> str:
    """List services in the given namespace with their type and selector"""
    ret = core_v1.list_namespaced_service(namespace=namespace)
    return "\n".join(
        f"{s.metadata.name}  {s.spec.type}  selector:{s.spec.selector}"
        for s in ret.items
    )
