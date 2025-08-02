import sys
import asyncio
import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


class UserManager:
    def __init__(self, json_path: str):
        self.json_path = json_path
        if not os.path.exists(self.json_path):
            with open(self.json_path, 'w') as f:
                json.dump([], f)

    def load_users(self) -> List[Dict]:
        with open(self.json_path, 'r') as f:
            return json.load(f)

    def save_users(self, users: List[Dict]):
        with open(self.json_path, 'w') as f:
            json.dump(users, f, indent=2)

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        return next((u for u in self.load_users() if u["id"] == user_id), None)

    def create_user(self, name: str) -> Dict:
        users = self.load_users()
        new_user = {
            "id": int(datetime.now().timestamp()),
            "name": name
        }
        users.append(new_user)
        self.save_users(users)
        return new_user

    def update_user(self, user_id: int, name: str) -> Optional[Dict]:
        users = self.load_users()
        for user in users:
            if user["id"] == user_id:
                user["name"] = name
                self.save_users(users)
                return user
        return None

    def delete_user(self, user_id: int) -> bool:
        users = self.load_users()
        filtered = [u for u in users if u["id"] != user_id]
        if len(filtered) == len(users):
            return False
        self.save_users(filtered)
        return True


server = Server("user-manager")
user_manager = UserManager("C:/Users/dell/Desktop/mcp_servers/users manager/users.json")


@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="createUser",
            description="Créer un nouvel utilisateur",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nom de l'utilisateur"}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="updateUser",
            description="Met à jour le nom d'un utilisateur existant",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"}
                },
                "required": ["id", "name"]
            }
        ),
        Tool(
            name="deleteUser",
            description="Supprime un utilisateur par ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {"type": "integer"}
                },
                "required": ["id"]
            }
        ),
        Tool(
            name="getAllUsers",
            description="Récupère la liste complète des utilisateurs",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    if name == "createUser":
        user = user_manager.create_user(arguments["name"])
        return [TextContent(type="text", text=f"✅ Utilisateur créé : {user}")]

    elif name == "updateUser":
        updated = user_manager.update_user(arguments["id"], arguments["name"])
        if updated:
            return [TextContent(type="text", text=f"🔄 Utilisateur mis à jour : {updated}")]
        return [TextContent(type="text", text="⚠️ Utilisateur non trouvé")]

    elif name == "deleteUser":
        success = user_manager.delete_user(arguments["id"])
        return [TextContent(type="text", text="🗑️ Utilisateur supprimé" if success else "⚠️ Utilisateur non trouvé")]

    elif name == "getAllUsers":
        users = user_manager.load_users()
        # On retourne la liste des utilisateurs en JSON dans un TextContent
        return [TextContent(type="text", text=json.dumps(users, indent=2))]

    return [TextContent(type="text", text="❌ Outil inconnu")]


async def main():
    initialization_options = InitializationOptions(
        server_name="UserManagerServer",
        server_version="1.0.0",
        capabilities=server.get_capabilities(NotificationOptions(), {})
    )
    async with stdio_server() as (read, write):
        await server.run(
            read_stream=read,
            write_stream=write,
            initialization_options=initialization_options
        )


if __name__ == "__main__":
    asyncio.run(main())
