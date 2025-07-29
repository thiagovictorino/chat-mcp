from importlib import import_module

# Ensure tool modules are imported when package is initialized
_module_names = [
    "mcp_server.tools.channel",
    "mcp_server.tools.agent",
    "mcp_server.tools.messaging",
]

for _name in _module_names:
    import_module(_name)