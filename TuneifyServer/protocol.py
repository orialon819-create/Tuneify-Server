"""
protocol.py

This module defines the Protocol class, which is responsible for
parsing raw messages from clients into a structured format.
It splits messages into a command name and a list of parameters.
"""

import json

class Protocol:
    def parse(self, message):
        try:
            # This turns the JSON string from Android into a Python Dictionary
            return json.loads(message)
        except Exception as e:
            print(f"Protocol Error: Could not parse JSON. Error: {e}")
            return {"command": None, "parameters": {}}
