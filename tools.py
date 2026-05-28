from langchain.tools import tool
from k8s import v1


@tool
def list_namespaces() -> str:
    """List namespaces"""
    ret = v1.list_namespace()
    return "\n".join(i.metadata.name for i in ret.items)
