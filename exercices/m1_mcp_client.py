"""
M1 — Client MCP minimal, sans Node : lance le serveur exercices/m1_mcp.py, liste ses
outils tels qu'un assistant IA les recoit, puis appelle simuler_pret.
C'est le meme protocole qu'utilisent Claude Desktop, un IDE ou un assistant d'entreprise.

    uv run python -m exercices.m1_mcp_client      # depuis la racine du repo
"""
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    serveur = StdioServerParameters(command=sys.executable, args=["-m", "exercices.m1_mcp"])
    async with stdio_client(serveur) as (lecture, ecriture):
        async with ClientSession(lecture, ecriture) as session:
            await session.initialize()

            outils = await session.list_tools()
            print("=== Outils exposes par le serveur MCP ===")
            for o in outils.tools:
                params = ", ".join(o.inputSchema.get("properties", {}))
                print(f"\n- {o.name}({params})")
                print("  " + (o.description or "").strip().replace("\n", "\n  "))

            print("\n=== Appel : simuler_pret(250000, 25, 3.4) ===")
            r = await session.call_tool("simuler_pret", {"montant": 250000, "duree_ans": 25, "taux_annuel_pct": 3.4})
            print(r.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
