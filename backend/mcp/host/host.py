class MCPHost:
    def __init__(self, servers: list):
        self.servers = servers

    async def collect_context(self, **kwargs) -> dict:
        context = {}

        print("\n[MCP] Incoming args:", kwargs)

        for server in self.servers:
            print("[MCP] Calling:", server.__class__.__name__)

            ctx = await server.get_context(**kwargs)

            print("[MCP] Returned:", ctx)

            context.update(ctx)

        return context
