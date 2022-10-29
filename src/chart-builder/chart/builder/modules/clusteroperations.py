from abc import ABC, abstractmethod
from rich.console import Console

from azure.identity import ClientSecretCredential
from azure.mgmt.containerservice import ContainerServiceClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.subscription import SubscriptionClient

import errno
import os
import platform
import stat
import tempfile
import time
import yaml

# GLOBAL VARIABLES
console = Console(color_system="standard")

#----------------------------------------
# Factory Class
#----------------------------------------

class ManagedClusterOperationsFactory():

    def __init__(self) -> None:
        self.factories = {
            "azure": AzureManagedClusterOperations()
        }
    
    def get(self, cluster_operations: str=None):
        try:
            factory = self.factories[cluster_operations]
        except KeyError as err:
            raise Exception(err)
        return factory

#----------------------------------------
# Implementation Classes
#----------------------------------------

class ManagedClusterOperations(ABC):

    @abstractmethod
    def build_cluster_admin_credentials(self) -> None:
        pass

class AzureManagedClusterOperations(ManagedClusterOperations):

    def build_cluster_admin_credentials(self, resource_group: str, cluster: str, 
                                            tenant_id: str, client_id: str, client_secret: str, 
                                            path=os.path.join(os.path.expanduser('~'), '.kube', 'config')) -> None:
        
        # Log it
        with console.status("Getting access credentials to managed Kubernetes cluster...", spinner="line") as status:

            # Slow Down for logging output
            time.sleep(2)

            # Set credentials
            credentials = ClientSecretCredential(tenant_id, client_id, client_secret, logging_enable=False)

            # Set Resource Group If Not Exist
            if resource_group is None: 
                resource_group = f'rg-do-{cluster}'

            # Subscription Client
            subscription_client = SubscriptionClient(credentials)

            # Get List of All Subscriptions
            sub_list = subscription_client.subscriptions.list()

            # Set Subscription Where Resource Group Exists
            for sub in sub_list:

                try:

                    # Resource Client
                    resource_client = ResourceManagementClient(credentials, sub.subscription_id)

                    # Check If Resource Group Exists
                    result_check = resource_client.resource_groups.check_existence(resource_group)
                    
                    # Success
                    if result_check:

                        # Set Subscription Id
                        subscription_id = sub.subscription_id

                # Next Loop
                except Exception:
                    pass

            # Connect to Azure Container Service
            container_service_client = ContainerServiceClient(credentials, subscription_id)

            # Get Kubeconfig
            kubeconfig = container_service_client.managed_clusters.list_cluster_admin_credentials(resource_group, cluster).kubeconfigs[0].value.decode(encoding='UTF-8')
            self._merge_credentials(kubeconfig, path, overwrite_existing=False)

    def _merge_credentials(self, kubeconfig, path, overwrite_existing=False):

        """Merge an unencrypted kubeconfig into the file at the specified self.path"""

        # ensure that at least an empty ~/.kube/config exists
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as ex:
                if ex.errno != errno.EEXIST:
                    raise Exception
        if not os.path.exists(path):
            with os.fdopen(os.open(path, os.O_CREAT | os.O_WRONLY, 0o600), 'wt'):
                pass

        # merge the new kubeconfig into the existing one
        fd, temp_path = tempfile.mkstemp()
        additional_file = os.fdopen(fd, 'w+t')
        try:
            additional_file.write(kubeconfig)
            additional_file.flush()
            self._merge_kubernetes_configurations(path, temp_path, overwrite_existing)
        except yaml.YAMLError as ex:
            console.print((f'[red]:cross_mark: [white]Failed to merge credentials to kube config file: %s', ex))
        finally:
            additional_file.close()
            os.remove(temp_path)

    def _merge_kubernetes_configurations(self, existing_file, addition_file, replace, context_name=None) -> None:

        existing = self._load_kubernetes_configuration(existing_file)
        addition = self._load_kubernetes_configuration(addition_file)

        if context_name is not None:
            addition['contexts'][0]['name'] = context_name
            addition['contexts'][0]['context']['cluster'] = context_name
            addition['clusters'][0]['name'] = context_name
            addition['current-context'] = context_name

        # rename the admin context so it doesn't overwrite the user context
        for ctx in addition.get('contexts', []):
            try:
                if ctx['context']['user'].startswith('clusterAdmin'):
                    admin_name = ctx['name'] + '-admin'
                    addition['current-context'] = ctx['name'] = admin_name
                    break
            except (KeyError, TypeError):
                continue

        if addition is None:
            raise Exception(f'failed to load additional configuration from {addition_file}')

        if existing is None:
            existing = addition
        else:
            self._handle_merge(existing, addition, 'clusters', replace)
            self._handle_merge(existing, addition, 'users', replace)
            self._handle_merge(existing, addition, 'contexts', replace)
            existing['current-context'] = addition['current-context']

        # check that ~/.kube/config is only read and writable by its owner
        if platform.system() != 'Windows':
            existing_file_perms = "{:o}".format(stat.S_IMODE(os.lstat(existing_file).st_mode))
            if not existing_file_perms.endswith('600'):
                console.print('%s has permissions "%s".\nIt should be readable and writable only by its owner.',
                            existing_file, existing_file_perms)

        with open(existing_file, 'w+') as stream:
            yaml.safe_dump(existing, stream, default_flow_style=False)

        current_context = addition.get('current-context', 'UNKNOWN')
        console.print(f'[bright_green]:heavy_check_mark: [white]Merged[/] [bright_green]"{current_context}"[/] [white]as current context in[/] [bright_magenta]{existing_file}[/]')

    def _load_kubernetes_configuration(self, filename) -> None:

        try:
            with open(filename) as stream:
                return yaml.safe_load(stream)
        except (IOError, OSError) as ex:
            if getattr(ex, 'errno', 0) == errno.ENOENT:
                raise Exception('{} does not exist'.format(filename))
            raise
        except (yaml.parser.ParserError, UnicodeDecodeError) as ex:
            raise Exception('Error parsing {} ({})'.format(filename, str(ex)))

    def _handle_merge(self, existing, addition, key, replace) -> None:
        if not addition.get(key, False):
            return
        if existing[key] is None:
            existing[key] = addition[key]
            return

        for i in addition[key]:
            for j in existing[key]:
                if not i.get('name', False) or not j.get('name', False):
                    continue
                if i['name'] == j['name']:
                    if replace or i == j:
                        existing[key].remove(j)
                    else:
                        msg = 'A different object named {} already exists in your kubeconfig file.\nOverwrite?'
                        overwrite = False
                        if overwrite:
                            existing[key].remove(j)
                        else:
                            msg = 'A different object named {} already exists in {} in your kubeconfig file.'
                            raise Exception(msg.format(i['name'], key))
            existing[key].append(i)