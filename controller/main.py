from kubernetes import client, config, watch
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def CreatePod(api_instance, namespace, name, image, script):
    try:
        # Define the pod specification
        container = client.V1Container(
            name=name,
            image=image,
            command=['python', '-c', script]  # Executes the script directly
        )
        pod_spec = client.V1PodSpec(containers=[container])
        metadata = client.V1ObjectMeta(name=name)
        pod = client.V1Pod(api_version='v1', kind='Pod', metadata=metadata, spec=pod_spec)

        # Create the pod
        api_instance.create_namespaced_pod(namespace=namespace, body=pod)
        logger.info(f"Pod created: {name}")
    except Exception as e:
        logger.info(f"Error with pod creation: {e}")

def main():
    # Load in-cluster configuration
    config.load_incluster_config()
    
    # Create a CustomObjectsApi client for interacting with CRDs
    custom_api = client.CustomObjectsApi()
    core_api = client.CoreV1Api()
    
    # Define CRD group, version, and plural
    crd_group = "learn-k8s.com"
    crd_version = "v1"
    crd_plural = "python-script-containers"

    # Create a Watch instance
    w = watch.Watch()
    
    logger.info("Starting to watch for custom resources...")

    # Watch for changes to the CRD resources
    for event in w.stream(custom_api.list_namespaced_custom_object,
                         group=crd_group,
                         version=crd_version,
                         namespace='default',  # Replace with your namespace
                         plural=crd_plural):
        obj = event['object']
        event_type = event['type']
        name = obj['metadata']['name']
        
        if event_type == 'ADDED':
            script = obj['spec'].get('script', '')
            image = obj['spec'].get('image', '')
            logger.info(f"New resource added: {name}")
            logger.info(f"Script: {script}")
            logger.info(f"Image: {image}")
            CreatePod(core_api, "default", name, image, script)
        elif event_type == 'MODIFIED':
            logger.info(f"Resource modified: {name}")
            # Log additional details if needed
        elif event_type == 'DELETED':
            logger.info(f"Resource deleted: {name}")
            # Log additional details if needed

if __name__ == '__main__':
    main()
