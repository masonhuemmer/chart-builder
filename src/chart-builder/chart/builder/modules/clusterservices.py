
from abc import ABC, abstractmethod
from rich.console import Console

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException

import base64
import json
import time

# GLOBAL VARIABLES
console = Console(color_system="standard")

#----------------------------------------
# Factory Class
#----------------------------------------

class ManagedClusterServicesFactory():

    def __init__(self) -> None:
        self.factories = {
            "azure": AzureManagedClusterServices()
        }
    
    def get(self, cluster_services: str=None):
        try:
            factory = self.factories[cluster_services]
        except KeyError as err:
            raise Exception(err)
        return factory

#----------------------------------------
# Implementation Classes
#----------------------------------------

class ManagedClusterServices(ABC):

    @abstractmethod
    def build_namespace(self) -> None:
        pass

    @abstractmethod
    def build_registery_credentials(self) -> None:
        pass

class AzureManagedClusterServices(ManagedClusterServices):

    def build_namespace(self, namespace) -> None:

        # Log it
        with console.status("Creating kubernetes namespace...", spinner="line") as status:

            # Slow Down for logging output
            time.sleep(2)

            # Start Timer
            if namespace is not None:

                # Load Kubeconfig
                config.load_kube_config()

                # Configure Client
                v1 = client.CoreV1Api()

                # Check if Namespace Exists
                field_selector = f'metadata.name={namespace}'
                result = v1.list_namespace(field_selector=field_selector).items

                if not result:
                    metadata=client.V1ObjectMeta(name=namespace)
                    v1.create_namespace(client.V1Namespace(metadata))
                else:
                    console.print(f'[bright_green]:heavy_check_mark:[/] [white]Namespace[/] [bright_green]"{namespace}"[/] [white]already exists[/]')

    def build_registery_credentials(self, name: str=None, registry: str=None, username: str=None, password: str=None, namespace: str=None, email: str = "someone@spreetail.com"):
    
        # Log it
        with console.status("Creating registry credentials...", spinner="line") as status:

            # Slow Down for logging output
            time.sleep(2)

            if name is not None:

                    # Load Kubeconfig
                    config.load_kube_config()

                    # Configure Client
                    v1 = client.CoreV1Api()

                    # Check Secret
                    try: 
                        result = v1.read_namespaced_secret(name, namespace)
                    except ApiException as err:
                        if err.status == 404: # Not found
                            result = None
                    
                    # If secret does not exist, create it
                    if result is None:

                        # Write docker config 
                        auth = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("utf-8")
                        docker_config_dict = {
                            "auths": {
                                registry: {
                                    "username": username,
                                    "password": password,
                                    "email": email,
                                    "auth": auth,
                                }
                            }
                        }

                        docker_config = base64.b64encode(
                            json.dumps(docker_config_dict).encode("utf-8")
                        ).decode("utf-8")

                        try: 
                            v1.create_namespaced_secret(
                                namespace=namespace,
                                body=client.V1Secret(
                                    metadata=client.V1ObjectMeta(
                                        name=name,
                                    ),
                                    type="kubernetes.io/dockerconfigjson",
                                    data={".dockerconfigjson": docker_config},
                                ),
                            )
                            console.print(f'[bright_green]:heavy_check_mark:[/] [white]Registry credentials[/] [bright_green]"{name}"[/] [white]created[/]')
                        except (ApiException, Exception) as err:
                            raise Exception(err)

                    else:
                        console.print(f'[bright_green]:heavy_check_mark:[/] [white]Registry credentials[/] [bright_green]"{name}"[/] [white]already exists[/]')
