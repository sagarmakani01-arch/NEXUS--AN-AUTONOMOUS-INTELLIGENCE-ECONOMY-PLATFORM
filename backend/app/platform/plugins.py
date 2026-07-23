import json
import uuid

from app.platform.persistence import platform_db
from app.domain.models.platform import Plugin, PluginDependency


class PluginSystem:
    """Manages installed plugins and extensions."""

    PLUGIN_PRESETS = [
        {"name": "advanced_economy", "display_name": "Advanced Economy Model", "type": "economic", "target": "economy", "desc": "Adds complex economic behaviors including inflation, credit markets, and business cycles."},
        {"name": "democratic_governance", "display_name": "Democratic Governance", "type": "governance", "target": "governance", "desc": "Implements voting, elections, and representative government systems."},
        {"name": "neural_reasoning", "display_name": "Neural Reasoning System", "type": "reasoning", "target": "agents", "desc": "Enhances agent reasoning with neural network-inspired decision making."},
        {"name": "climate_dynamics", "display_name": "Climate Dynamics", "type": "environmental", "target": "world", "desc": "Adds detailed climate modeling with temperature, precipitation, and seasonal patterns."},
        {"name": "tech_tree_expanded", "display_name": "Expanded Technology Tree", "type": "technology", "target": "research", "desc": "Adds 50+ new technologies across 12 domains with branching paths."},
        {"name": "visualization_3d", "display_name": "3D Visualization Layer", "type": "visualization", "target": "visual", "desc": "Three-dimensional world rendering with camera controls and terrain."},
        {"name": "space_expansion", "display_name": "Space Expansion", "type": "physics", "target": "world", "desc": "Enables space exploration, colonization, and interstellar travel."},
        {"name": "education_reform", "display_name": "Education System Overhaul", "type": "economic", "target": "economy", "desc": "Detailed education model with schools, universities, and specialization tracks."},
    ]

    async def install(self, name: str, display_name: str = None, plugin_type: str = "custom", target: str = None) -> dict:
        existing = await platform_db.get_plugins(plugin_type=plugin_type)
        if any(p.name == name for p in existing):
            return {"error": f"Plugin '{name}' already installed"}

        plugin = Plugin(
            name=name, display_name=display_name or name,
            description=f"Plugin: {display_name or name}",
            author="nexus",
            version="1.0.0", plugin_type=plugin_type, target=target,
            entry_point=f"plugins.{name}.main",
            config_schema=json.dumps({"enabled": True, "settings": {}}),
            enabled=True,
        )
        saved = await platform_db.create_plugin(plugin)
        return {"id": saved.id, "name": saved.name, "enabled": True}

    async def install_presets(self) -> list[dict]:
        results = []
        for preset in self.PLUGIN_PRESETS:
            result = await self.install(preset["name"], preset["display_name"], preset["type"], preset["target"])
            results.append(result)
        return results

    async def list_plugins(self, enabled: bool = None) -> list[dict]:
        plugins = await platform_db.get_plugins(enabled)
        result = []
        for p in plugins:
            deps = await platform_db.get_dependencies(p.id)
            result.append({
                "id": p.id, "name": p.name, "display_name": p.display_name,
                "description": p.description, "author": p.author, "version": p.version,
                "type": p.plugin_type, "target": p.target, "enabled": p.enabled,
                "dependencies": [{"name": d.dependency_name, "min_version": d.min_version, "optional": d.optional} for d in deps],
            })
        return result

    async def toggle(self, plugin_id: str, enabled: bool) -> dict:
        p = await platform_db.update_plugin(plugin_id, enabled=enabled)
        if not p: return {"error": "Plugin not found"}
        return {"id": p.id, "name": p.name, "enabled": p.enabled}

    async def get_stats(self) -> dict:
        all_p = await platform_db.get_plugins()
        enabled = sum(1 for p in all_p if p.enabled)
        types = {}
        for p in all_p:
            types[p.plugin_type] = types.get(p.plugin_type, 0) + 1
        return {"total": len(all_p), "enabled": enabled, "disabled": len(all_p) - enabled, "types": types}


plugin_system = PluginSystem()
