from kubernetes import client, config

try:
    config.load_incluster_config()
except config.ConfigException:
    config.load_kube_config()

core_v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()
