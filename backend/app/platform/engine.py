from app.platform.plugins import plugin_system
from app.platform.sdk import sdk
from app.platform.modules import marketplace
from app.platform.templates import template_manager
from app.platform.scenarios import scenario_builder
from app.platform.workspace import workspace_manager
from app.platform.data_export import data_exporter
from app.platform.collaboration import collaboration


class PlatformEngine:
    """Orchestrates the extension and platform ecosystem."""

    def __init__(self):
        self._initialized = False

    async def initialize(self):
        if self._initialized:
            return
        await plugin_system.install_presets()
        await template_manager.seed()
        await marketplace.seed_modules()
        await sdk.init_tools()
        self._initialized = True

    async def get_full_state(self) -> dict:
        if not self._initialized:
            await self.initialize()
        return {
            "initialized": self._initialized,
            "plugins": await plugin_system.get_stats(),
            "marketplace": await marketplace.get_stats(),
            "templates": len(await template_manager.list_templates()),
            "scenarios": len(await scenario_builder.list_scenarios()),
            "tools": len(await sdk.get_tools()),
        }


platform_engine = PlatformEngine()
