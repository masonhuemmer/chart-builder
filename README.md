# Chart Builder

[](https://user-images.githubusercontent.com/49791141/198853420-98979b6f-9b99-48c0-9ed4-453e1080ebe8.mp4)

### What Is It?
This python package is broken up into four stages. 
1. Getting access credentials to managed Kubernetes cluster (i.e. kubeconfig)
2. Running required steps before deployment (i.e. create namespace)
3. Running the package manager deployment (i.e. helm)
4. Report deployment status to observability platform (i.e. datadog)

### Arguments

```
usage: chart.builder [-h] [--department-name DEPARTMENT_NAME]
                   [--department-team DEPARTMENT_TEAM] [--app-name APP_NAME]
                   [--team APP_TEAM] [--version APP_VERSION]
                   [--environment ENVIRONMENT]
                   [--reporting-platform REPORTING_PLATFORM]
                   [--clustername AKS_CLUSTER_NAME]
                   [--resource-group AKS_CLUSTER_RESOURCE_GROUP]
                   [--client-id AKS_SERVICE_PRINCIPAL_ID]
                   [--client-secret AKS_SERVICE_PRINCIPAL_PASSWORD]
                   [--tenant AZURE_TENANT_ID]
                   [--docker-registry DOCKER_REGISTRY]
                   [--docker-username DOCKER_USERNAME]
                   [--docker-password DOCKER_PASSWORD]
                   [--pull-secret-name PULL_SECRET_NAME]
                   [--repository HELM_REPOSITORY] [--chart HELM_CHART]
                   [--release RELEASE] [--namespace NAMESPACE]
                   [--helm-values HELM_VALUES] [--helm-set HELM_SETS]
                   [--helm-atomic HELM_ATOMIC] [--helm-timeout HELM_TIMEOUT]
                   [--helm-wait HELM_WAIT] [--helm-version HELM_VERSION]
                   [--new-relic-app-name NEW_RELIC_APP_NAME]

Logs into platform hosting kubernetes, generates a kubeconfig, and installs a helm chart.

optional arguments:
  -h, --help            show this help message and exit

Default arguments:
  --department-name DEPARTMENT_NAME
                        The department that owns the application.
  --department-team DEPARTMENT_TEAM
                        The department team who owns the application.
  --app-name APP_NAME   Name of the application.
  --team APP_TEAM       Application Team.
  --version APP_VERSION, --app-version APP_VERSION
                        Version of the application.
  --environment ENVIRONMENT
                        Where the application is deployed.
  --reporting-platform REPORTING_PLATFORM
                        The reporting platform where events are posted (Datadog, NewRelic, Local).

Azure arguments:
  --clustername AKS_CLUSTER_NAME, --aksclustername AKS_CLUSTER_NAME
                        Name of the Managed Kubernetes Cluster.
  --resource-group AKS_CLUSTER_RESOURCE_GROUP, --aksclusterresourcegroup AKS_CLUSTER_RESOURCE_GROUP
                        Name of resource group.
  --client-id AKS_SERVICE_PRINCIPAL_ID, --username AKS_SERVICE_PRINCIPAL_ID
                        Service principal ID.
  --client-secret AKS_SERVICE_PRINCIPAL_PASSWORD, --password AKS_SERVICE_PRINCIPAL_PASSWORD
                        Service principal Secret.
  --tenant AZURE_TENANT_ID, --tenant-id AZURE_TENANT_ID
                        The AAD tenant, must provide when using service principals.

Docker arguments:
  --docker-registry DOCKER_REGISTRY, --container-registry DOCKER_REGISTRY
                        Host where container images are stored.
  --docker-username DOCKER_USERNAME
                        Username to authenticate to the Container registry.
  --docker-password DOCKER_PASSWORD
                        Password to authenticate to the Container registry.
  --pull-secret-name PULL_SECRET_NAME
                        Name for Docker Registry Secret.

Helm arguments:
  --repository HELM_REPOSITORY, --helm-repository HELM_REPOSITORY
                        A repository to the chart, packaged, or fully qualified URL.
  --chart HELM_CHART, --helm-chart HELM_CHART
                        A path to a chart directory, a packaged chart, or a fully qualified URL.
  --release RELEASE, --helm-release RELEASE
                        Release name for a chart instance installed in Kubernetes.
  --namespace NAMESPACE, --helm-namespace NAMESPACE
                        Namespace scope for this request.
  --helm-values HELM_VALUES
                        Specify values in a YAML file or a URL (can specify multiple)
  --helm-set HELM_SETS  Set values on the command line (can specify multiple or separate values with commas: key1=val1,key2=val2)
  --helm-atomic HELM_ATOMIC
                        If set, upgrade process rolls back changes made in case of failed upgrade. The --wait flag will be set automatically if --atomic is used
  --helm-timeout HELM_TIMEOUT
                        time to wait for any individual Kubernetes operation (like Jobs for hooks) (default 5m0s)
  --helm-wait HELM_WAIT
                        Time to wait for any individual Kubernetes operation (like Jobs for hooks) (default 5m0s)
  --helm-version HELM_VERSION
                        Specify a version constraint for the chart version to use. This constraint can be a specific tag (e.g. 1.1.1) or it may reference a valid
                        range (e.g. ^2.0.0). If this is not specified, the latest version is used.

Legacy arguments:
  --new-relic-app-name NEW_RELIC_APP_NAME
                        Name of the application to be reported to New Relic.

```

### PDM
This python package is using PDM (https://pdm.fming.dev/latest/) package manager.

To initilize the project, run the following command.

```
cd src/chart-builder/
pdm sync
```

To run the project, run the following command.

>This command loads .env files at runtime and then runs the `chart.builder` package.

```
cd src/chart-builder/
pdm run chart-builder
```

This command is configured in the pyproject.toml file.

### Dotenv Files
The python package supports environment variables. 
With the support of PDM, you are able to load your variables through a dotenv file.

Recommend you create a <b>.env.local</b> in the *src/chart-builder* directory.

```
APP_NAME=chart.builder
APP_TEAM=shared.services
APP_VERSION=1.0.0
ENVIRONMENT=dev
REPORTING_PLATFORM=datadog
AKS_CLUSTER_NAME=
AKS_CLUSTER_RESOURCE_GROUP=
AKS_SERVICE_PRINCIPAL_ID=
AKS_SERVICE_PRINCIPAL_PASSWORD=
AZURE_TENANT_ID=
HELM_REPOSITORY=helm
HELM_CHART=helm
RELEASE=
NAMESPACE=
```

### Pipelines

```
  script:
    - >
      chart-builder
      --aksclustername="${CLUSTER_NAME}"
      --app-name="${RELEASE_NAME}"
      --version="${RELEASE_VERSION}"
      --environment="${ENVIRONMENT}"
      --team="${DEPARTMENT_TEAM}"
      --release="${RELEASE_NAME}"
      --department-name="${DEPARTMENT_NAME}"
      --department-team="${DEPARTMENT_TEAM}"
      --docker-registry=${DOCKER_REGISTRY}
      --docker-username=${DOCKER_USERNAME}
      --docker-password=${DOCKER_PASSWORD}
      --helm-chart=${HELM_CHART_DIRECTORY}
      --helm-values=${HELM_VALUES_FILE}
      --helm-set=--history-max=4  
      --helm-set=namespace=${NAMESPACE}
      --helm-set=cluster=${CLUSTER_NAME}
      --helm-set=image.repository=${DOCKER_REGISTRY}/${DOCKER_REPOSITORY}/${RELEASE_NAME}
      --helm-set=image.tag="${RELEASE_VERSION}"
      --helm-set=image.pullSecret=azure
      --helm-set=newRelic.licenseKey="${NEW_RELIC_LICENSE_KEY}"
      --helm-set=newRelic.appName="${NEW_RELIC_APP_NAME}"
      --helm-set=azureClientId="${AZURE_CLIENT_ID}"
      --helm-set=azureClientSecret="${AZURE_CLIENT_SECRET}"
      --helm-set=azureTenantId="${AZURE_TENANT_ID}"
      --helm-set=azureAppConfigUrl="${AZURE_APP_CONFIG_URL}"
```

### Organizational Architecture
<b>Package:</b> `/src/chart-builder`

<b>Entrypoint:</b> `/src/chart-builder/chart/builder/__main__.py`

<b>Local Modules:</b> `/src/chart-builder/chart/builder/modules`
- *arguments.py*
- *logger.py*
- *clusteroperations.py*
- *clusterservices.py*
- *packagemanager.py*
- *reportingservices.py*

### Modules

<b>arguments.py:</b> Configures parser for command-line options, arguments and sub-commands
- *EnvDefault* Class
- *get_parser* moethod

<b>clusteroperations.py:</b> Interface classes and subclasses that handles the implementationn of the `ManagedClusterOperations' class.
- *ManagedClusterOperationsFactory* factory class
- *ManagedClusterOperations* abstract class
- *AzureManagedClusterOperations(ManagedClusterOperations)* class

<b>clusterservices.py:</b> Interface classes and subclasses that handles the implementationn of the `ManagedClusterServices' class.
- *ManagedClusterServicesFactory* factory class
- *AzureManagedClusterServices* abstract class
- *AzureManagedClusterServices(ManagedClusterServices)* class

<b>reportingservices.py:</b> Interface classes and subclasses that handles the implementationn of the `Reporter' class.
- *ReporterFactory* factory class
- *Reporter* abstract class
- *Datadog(Reporter)* implementation class
- *NewRelic(Reporter)* implementation class
- *Local(Reporter)* implementation class

<b>packagemanager.py:</b> Interface classes and subclasses that handles the implementationn of the `PackageManager' class.
- *PackageManagerFactory* factory class
- *PackageManager* abstract class 
- *HelmPackageManager(PackageManager)* class (Implementation)
