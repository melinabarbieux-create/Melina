"""
M1 — Demo MCP : les outils NidBuyer exposes comme serveur MCP.

Le meme code que backend/outils.py, sans rien reecrire : tout client MCP
(Claude Desktop, un IDE, un assistant d'entreprise) peut alors les appeler.

    npx @modelcontextprotocol/inspector uv run python -m exercices.m1_mcp   # depuis la racine du repo

Sans Node (ou si npx n'a pas de reseau) : uv run python -m exercices.m1_mcp_client
fait la meme chose dans le terminal.

L'inspecteur liste les outils (nom, description = docstring, parametres types)
et permet de les appeler a la main : c'est exactement ce que voit un modele.
"""
from mcp.server.fastmcp import FastMCP

from backend.outils import chercher_biens, ecart_au_marche, simuler_pret

mcp = FastMCP("nidbuyer")
for outil in (chercher_biens, ecart_au_marche, simuler_pret):
    mcp.tool()(outil)

if __name__ == "__main__":
    mcp.run()  # transport stdio par defaut
