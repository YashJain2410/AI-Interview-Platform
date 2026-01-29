class MCPHost:
    def __init__(self, servers: list):
        self.servers = servers

    async def collect_context(self, **kwargs) -> dict:
        context = {}

        for server in self.servers:
            server_ctx = await server.get_context(**kwargs)
            context.update(server_ctx)

        return context