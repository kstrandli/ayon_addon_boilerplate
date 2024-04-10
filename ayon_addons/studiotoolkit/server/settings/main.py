from pydantic import Field

from ayon_server.settings import BaseSettingsModel

class StudioToolkitSettings(BaseSettingsModel):

    template_project_name: str = Field(
        default="",
        title="TemplateProjectName",
        description="Project Name used for templates",
        example="MyProject",
        scope=["studio"]
    )

DEFAULT_VALUES = {
    "template_project_name": "MyProject",
}