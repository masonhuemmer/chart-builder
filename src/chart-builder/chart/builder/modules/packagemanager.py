
from abc import ABC, abstractmethod

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

import os
import re
import subprocess
import time
import textwrap

# GLOBAL VARIABLES
console = Console(color_system="standard")
text = Text(no_wrap=True, overflow="ellipsis")

#----------------------------------------
# Factory Class
#----------------------------------------

class PackageManagerFactory():

    def __init__(self) -> None:
        self.factories = {
            "helm": HelmPackageManager()
        }
    
    def get(self, package_manager: str=None):
        try:
            factory = self.factories[package_manager]
        except KeyError as err:
            raise Exception(err)
        return factory

#----------------------------------------
# Implementation Classes
#----------------------------------------

class PackageManager(ABC):  

    @abstractmethod
    def build(self) -> None:
        pass

    @abstractmethod
    def deploy(self) -> None:
        pass

class HelmPackageManager(PackageManager):

    def build(self, release: str, chart: str, repository: str, version: str, namespace: str, 
                    values: list, sets: list, atomic: str, timeout: str, wait: str, 
                    path=os.path.join(os.path.expanduser('~'), '.kube', 'config')):

        with console.status("Building package manager CLI command...", spinner="line") as status:
            
            # Slow Down for logging output
            time.sleep(2)
            
            # Build 'helm upgrade' command:
            command = [
                "helm",
                "upgrade",
                "--install",
                release,
                chart
            ]

            if version is not None:
                command.extend(["--version", version])

            if namespace is not None:
                command.extend(["--namespace", namespace])

            if repository is not None:
                command.extend(["--repo",repository])

            if values is not None:
                for value in values:
                    command.extend(["--values", value])

            if sets is not None:
                for helm_set in sets:
                    command.extend(["--set", helm_set])

            # Remaining parameters
            command.extend(["--kubeconfig", path, "--reset-values"])

            if timeout is not None:
                command.extend(["--timeout", timeout])

            if atomic is not None:
                command.append("--atomic")

            if wait is not None:
                command.append("--wait")

            self.print(command)
            return command

    def print(self, command: list):

            output_command = []

            for idx, line in enumerate(command):
                
                # First 5 lines
                if idx == 4:

                    # helm upgrade --install [release] [chart]
                    text.append(f"{command[idx-4]} {command[idx-3]} {command[idx-2]} ", style="white") 
                    text.append(f"{command[idx-1]} ", style="bright_green")
                    text.append(f"{command[idx]}\n", style="bright_magenta")

                # General style
                elif command[idx] in [ "--namespace", "--version", "--repo", "--timeout" ]:
                    text.append(f"{command[idx]} ", style="white")
                    text.append(f"{command[idx+1]}\n", style="bright_green")

                # Path style
                elif command[idx] in [ "--values", "--kubeconfig" ]:
                    text.append(f"{command[idx]} ", style="white")
                    text.append(f"{command[idx+1]}\n", style="bright_magenta")

                # Single key parameters, no value
                elif command[idx] in [ "--atomic", "--reset-values"]:
                    text.append(f"{command[idx]}\n", style="white")

                # Set style
                elif command[idx] in [ "--set" ]:

                    # Pattern Matching
                    set_command = re.split("=(.*)$", command[idx+1])

                    # Append Text
                    text.append(f"{command[idx]} ", style="white")
                    text.append(f"{set_command[0]}", style="bright_green")
                    text.append("=", style="white")
                    text.append(f"{set_command[1]}\n", style="bright_cyan")

            # Remove Whitespace / New Line EOL
            text.rstrip()

            # Log it
            console.print('[bright_green]:heavy_check_mark:[/] [white]Package manager CLI command:[/]')

            # Print Command
            console.print(Panel.fit(text, box=box.SIMPLE, padding=(0,1,0,5)), style="italic")
            
    def deploy(self, command: list):
        """Pass in command to subprocess. Output results."""

        # Log it
        with console.status("Running package manager CLI command...", spinner="line") as status:
            
            # Slow Down for logging output
            time.sleep(2)

            # Run command
            result = subprocess.run(command, capture_output=True, text=True)

            # If Error
            if result.stderr and result.returncode:
                raise Exception(result.stderr)
            elif result.stderr:
                console.print(result.stderr, style="red")

            # If Success
            if result.stdout:
                console.print("[bright_green]:heavy_check_mark:[/] [white]Package manager CLI output:[/]")
                console.print(Panel.fit(f"[bright_green]{result.stdout.rstrip()}[/]", box=box.SIMPLE, padding=(0,1,0,5)))

