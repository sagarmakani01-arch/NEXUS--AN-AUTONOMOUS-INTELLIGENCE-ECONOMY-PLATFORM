import json
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory as AsyncSessionLocal
from app.domain.models.platform import (
    Plugin, PluginDependency, SimulationTemplate, Scenario,
    ExtensionModule, Dataset, ExperimentWorkspace, CollaborationSession, DeveloperTool,
)


class PlatformPersistence:
    @staticmethod
    async def create_plugin(rec: Plugin) -> Plugin:
        async with AsyncSessionLocal() as s: s.add(rec); await s.commit(); await s.refresh(rec); return rec

    @staticmethod
    async def get_plugin(plugin_id: str) -> Optional[Plugin]:
        async with AsyncSessionLocal() as s: return await s.get(Plugin, plugin_id)

    @staticmethod
    async def get_plugins(enabled: bool = None, plugin_type: str = None) -> list[Plugin]:
        async with AsyncSessionLocal() as s:
            q = select(Plugin)
            if enabled is not None: q = q.where(Plugin.enabled == enabled)
            if plugin_type: q = q.where(Plugin.plugin_type == plugin_type)
            r = await s.execute(q.order_by(Plugin.name)); return list(r.scalars().all())

    @staticmethod
    async def update_plugin(pid: str, **kw) -> Optional[Plugin]:
        async with AsyncSessionLocal() as s:
            p = await s.get(Plugin, pid)
            if not p: return None
            for k, v in kw.items(): setattr(p, k, v)
            await s.commit(); await s.refresh(p); return p

    @staticmethod
    async def add_dependency(d: PluginDependency) -> PluginDependency:
        async with AsyncSessionLocal() as s: s.add(d); await s.commit(); await s.refresh(d); return d

    @staticmethod
    async def get_dependencies(plugin_id: str) -> list[PluginDependency]:
        async with AsyncSessionLocal() as s:
            r = await s.execute(select(PluginDependency).where(PluginDependency.plugin_id == plugin_id)); return list(r.scalars().all())

    @staticmethod
    async def create_template(t: SimulationTemplate) -> SimulationTemplate:
        async with AsyncSessionLocal() as s: s.add(t); await s.commit(); await s.refresh(t); return t

    @staticmethod
    async def get_templates(template_type: str = None) -> list[SimulationTemplate]:
        async with AsyncSessionLocal() as s:
            q = select(SimulationTemplate)
            if template_type: q = q.where(SimulationTemplate.template_type == template_type)
            r = await s.execute(q.order_by(SimulationTemplate.name)); return list(r.scalars().all())

    @staticmethod
    async def create_scenario(s: Scenario) -> Scenario:
        async with AsyncSessionLocal() as s: s.add(s); await s.commit(); await s.refresh(s); return s

    @staticmethod
    async def get_scenarios(public: bool = None, author_id: str = None) -> list[Scenario]:
        async with AsyncSessionLocal() as s:
            q = select(Scenario)
            if public is not None: q = q.where(Scenario.is_public == public)
            if author_id: q = q.where(Scenario.author_id == author_id)
            r = await s.execute(q.order_by(Scenario.created_at.desc())); return list(r.scalars().all())

    @staticmethod
    async def create_module(m: ExtensionModule) -> ExtensionModule:
        async with AsyncSessionLocal() as s: s.add(m); await s.commit(); await s.refresh(m); return m

    @staticmethod
    async def get_modules(category: str = None) -> list[ExtensionModule]:
        async with AsyncSessionLocal() as s:
            q = select(ExtensionModule)
            if category: q = q.where(ExtensionModule.category == category)
            r = await s.execute(q.order_by(ExtensionModule.downloads.desc())); return list(r.scalars().all())

    @staticmethod
    async def create_dataset(d: Dataset) -> Dataset:
        async with AsyncSessionLocal() as s: s.add(d); await s.commit(); await s.refresh(d); return d

    @staticmethod
    async def get_datasets(dataset_type: str = None) -> list[Dataset]:
        async with AsyncSessionLocal() as s:
            q = select(Dataset)
            if dataset_type: q = q.where(Dataset.dataset_type == dataset_type)
            r = await s.execute(q.order_by(Dataset.exported_at.desc())); return list(r.scalars().all())

    @staticmethod
    async def create_workspace(w: ExperimentWorkspace) -> ExperimentWorkspace:
        async with AsyncSessionLocal() as s: s.add(w); await s.commit(); await s.refresh(w); return w

    @staticmethod
    async def get_workspaces(owner_id: str = None) -> list[ExperimentWorkspace]:
        async with AsyncSessionLocal() as s:
            q = select(ExperimentWorkspace)
            if owner_id: q = q.where(ExperimentWorkspace.owner_id == owner_id)
            r = await s.execute(q.order_by(ExperimentWorkspace.updated_at.desc())); return list(r.scalars().all())

    @staticmethod
    async def join_session(s: CollaborationSession) -> CollaborationSession:
        async with AsyncSessionLocal() as s: s.add(s); await s.commit(); await s.refresh(s); return s

    @staticmethod
    async def get_session_users(workspace_id: str) -> list[CollaborationSession]:
        async with AsyncSessionLocal() as s:
            r = await s.execute(select(CollaborationSession).where(CollaborationSession.workspace_id == workspace_id)); return list(r.scalars().all())

    @staticmethod
    async def create_tool(t: DeveloperTool) -> DeveloperTool:
        async with AsyncSessionLocal() as s: s.add(t); await s.commit(); await s.refresh(t); return t

    @staticmethod
    async def get_tools(tool_type: str = None) -> list[DeveloperTool]:
        async with AsyncSessionLocal() as s:
            q = select(DeveloperTool)
            if tool_type: q = q.where(DeveloperTool.tool_type == tool_type)
            r = await s.execute(q.order_by(DeveloperTool.name)); return list(r.scalars().all())


platform_db = PlatformPersistence()
