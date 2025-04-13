from typing import Callable, Dict
import logging

logging.basicConfig(level=logging.INFO)
 
class SecurityPlugins:
    def __init__(self):
        self.plugins = []

    def register(self, plugin: Callable):
        self.plugins.append(plugin)
        logging.info(f"Registered security plugin: {plugin.__name__}")

    def apply(self, event: Dict):
        for plugin in self.plugins:
            plugin(event)