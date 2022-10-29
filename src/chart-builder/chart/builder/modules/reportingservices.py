
from abc import ABC, abstractmethod
from rich.console import Console

from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.events_api import EventsApi
from datadog_api_client.v1.model.event_alert_type import EventAlertType
from datadog_api_client.v1.model.event_create_request import EventCreateRequest

import gzip
import json
import os
import requests
import sys
import time

# GLOBAL VARIABLES
console = Console(color_system="standard")

#----------------------------------------
# Factory Class
#----------------------------------------

class ReportingServicesFactory():

    def __init__(self) -> None:
        self.factories = {
            "datadog": Datadog(),
            "newrelic": NewRelic(),
            "local": Local()
        }

    def get(self, reporter): 
        """Constructs a monitoring platform services factory based on implementation"""
        try:
            factory = self.factories[reporter]
        except KeyError:
            console.print(f'[white]Reporting platform[/] [green]"{reporter}"[/] [white]not supported.[/]')
            factory = self.factories["local"]
        return factory

#----------------------------------------
# Implementation Classes
#----------------------------------------

class ReportingServices(ABC):

    @abstractmethod
    def post_event(self) -> None:
        pass

class Datadog(ReportingServices):

    def post_event(self, devops_platform="Gitlab", event_message="Successfully deployed.", event_status="success", **kwargs) -> None:

        # Log it
        with console.status("Reporting deployment status...", spinner="line") as status:
            
            # Slow Down for logging output
            time.sleep(2)

            # Set Event Title and Message        
            event_title = f'Event on pipelines from {devops_platform.capitalize()}'

            # Set Event Title
            event_tags = []
            for key, value in kwargs.items():
                event_tags.append(f'{key}:{value}')

            if devops_platform == "Gitlab":

                # Set Source Type Name - https://docs.datadoghq.com/integrations/faq/list-of-api-source-attribute-value/
                event_tags.append(f'source:{devops_platform}') 

                # Predefined Variables - https://docs.gitlab.com/ee/ci/variables/predefined_variables.html
                event_tags.append(f'ci-pipeline-id:{os.environ.get("CI_PIPELINE_ID")}')
                event_tags.append(f'ci-pipeline-url:{os.environ.get("CI_PIPELINE_URL")}')
                event_tags.append(f'ci-pipeline-created-at:{os.environ.get("CI_PIPELINE_CREATED_AT")}')
                event_tags.append(f'ci-pipeline-source:{os.environ.get("CI_PIPELINE_SOURCE")}')

            # Set Alert Type
            alert_type = EventAlertType(
                value = event_status,
            )

            # EventCreateRequest - https://docs.datadoghq.com/api/latest/events/#post-an-event 
            body = EventCreateRequest(
                title = event_title,
                text = event_message,
                tags = event_tags,
                source_type_name = devops_platform,
                alert_type = alert_type,
            )

            # Post Event to Datadog Events API
            configuration = Configuration() # Loads environment variables
            with ApiClient(configuration) as api_client:
                api_instance = EventsApi(api_client)
                response = api_instance.create_event(body=body)

            if event_status == "error":
                console.print_exception(extra_lines=5, show_locals=True)
                sys.exit(1)
            else:
                console.print("[bright_green]:heavy_check_mark:[/] [white]Deployment status reported to Datadog[/]")

class NewRelic(ReportingServices):

    def post_event(self, devops_platform="Gitlab", event_message="Successfully deployed.", event_status="success", **kwargs) -> None:

        # Log it
        with console.status("Reporting deployment status...", spinner="line") as status:
            
            # Slow Down for logging output
            time.sleep(2)

            url = f'https://insights-collector.newrelic.com/v1/accounts/{os.environ.get("NEW_RELIC_ACCOUNT_ID")}/events'

            headers = {
                "Content-Type": "application/json",
                "X-Insert-Key": os.environ.get("NEW_RELIC_INSERT_KEY"),
                "Content-Encoding": "gzip",
            }

            content = {
                "eventType": "Deployments",
                "source":"gitlab",
                "status": event_status,
                "success": "1" if event_status == "success" else "0",
                "message":f'{event_message}'
            }

            for key, value in kwargs.items():
                if key == "service":
                    content["app_name"] = f'{value}'
                else:
                    content[key] = f'{value}'

            if devops_platform == "Gitlab":
                content['ci-pipeline-id'] = os.environ.get("CI_PIPELINE_ID")
                content["ci-pipeline-url"] = os.environ.get("CI_PIPELINE_URL")
                content["ci-pipeline-created-at"] = os.environ.get("CI_PIPELINE_CREATED_AT")
                content["ci-pipeline-source"] = os.environ.get("CI_PIPELINE_SOURCE")
            
            response = requests.post(url, headers=headers, data=gzip.compress(json.dumps(content).encode('utf-8')),)

            if event_status == "error":
                console.print_exception(extra_lines=5, show_locals=True)
                sys.exit(1)
            else:
                console.print("[bright_green]:heavy_check_mark:[/] [white]Deployment status reported to New Relic[/]")

class Local(ReportingServices):

    def post_event(self, devops_platform="Gitlab", event_message="Successfully deployed.", event_status="success", **kwargs) -> None:

        if event_status == "error":
            console.print_exception(extra_lines=5, show_locals=True)
            sys.exit(1)