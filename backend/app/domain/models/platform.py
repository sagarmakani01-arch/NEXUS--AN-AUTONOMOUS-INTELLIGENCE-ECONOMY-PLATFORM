import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, func

from app.core.database import Base


class Plugin(Base):
    __tablename__ = "platform_plugins"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    author = Column(String(255), nullable=True)
    version = Column(String(50), default="1.0.0")
    plugin_type = Column(String(100), nullable=False)
    target = Column(String(100), nullable=True)
    entry_point = Column(String(500), nullable=True)
    config_schema = Column(Text, default="{}")
    enabled = Column(Boolean, default=False)
    installed_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PluginDependency(Base):
    __tablename__ = "plugin_dependencies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plugin_id = Column(String(36), nullable=False, index=True)
    dependency_plugin_id = Column(String(36), nullable=False)
    dependency_name = Column(String(255), nullable=False)
    min_version = Column(String(50), default="1.0.0")
    optional = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SimulationTemplate(Base):
    __tablename__ = "simulation_templates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    template_type = Column(String(100), nullable=False)
    initial_conditions = Column(Text, default="{}")
    rules = Column(Text, default="{}")
    environment = Column(Text, default="{}")
    objectives = Column(Text, default="[]")
    recommended_plugins = Column(Text, default="[]")
    difficulty = Column(String(50), default="medium")
    author = Column(String(255), nullable=True)
    version = Column(String(50), default="1.0.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Scenario(Base):
    __tablename__ = "simulation_scenarios"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    template_id = Column(String(36), nullable=True)
    author_id = Column(String(36), nullable=True)
    is_public = Column(Boolean, default=True)
    config = Column(Text, default="{}")
    tags = Column(Text, default="[]")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ExtensionModule(Base):
    __tablename__ = "extension_modules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    author = Column(String(255), nullable=True)
    version = Column(String(50), default="1.0.0")
    source = Column(String(255), nullable=True)
    license = Column(String(100), default="MIT")
    category = Column(String(100), nullable=False)
    compatibility = Column(String(100), nullable=True)
    dependencies = Column(Text, default="[]")
    downloads = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Dataset(Base):
    __tablename__ = "exported_datasets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    dataset_type = Column(String(100), nullable=False)
    format = Column(String(50), default="json")
    simulation_id = Column(String(36), nullable=True)
    data = Column(Text, default="{}")
    record_count = Column(Integer, default=0)
    size_bytes = Column(Integer, default=0)
    exported_at = Column(DateTime(timezone=True), server_default=func.now())


class ExperimentWorkspace(Base):
    __tablename__ = "experiment_workspaces"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(String(36), nullable=True)
    configuration = Column(Text, default="{}")
    status = Column(String(50), default="draft")
    tags = Column(Text, default="[]")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CollaborationSession(Base):
    __tablename__ = "collaboration_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=False)
    role = Column(String(50), default="viewer")
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class DeveloperTool(Base):
    __tablename__ = "developer_tools"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    tool_type = Column(String(100), nullable=False)
    endpoint = Column(String(500), nullable=True)
    enabled = Column(Boolean, default=True)
    config = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
