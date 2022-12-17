# This file contains the main global variables for configuring a system

from asentaja.main import FileMapping


file_mappings: dict[str, FileMapping] = {}
packages: list[str] = []
enabled_services: list[str] = []

