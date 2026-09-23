"""Third Reality Siren device quirk - ZHA."""

from typing import Final

from zigpy.quirks import CustomCluster
from zigpy.quirks.v2 import QuirkBuilder
import zigpy.types as t
from zigpy.zcl.clusters.general import LevelControl
from zigpy.zcl.foundation import BaseAttributeDefs, ZCLAttributeDef


class SirenLevelControl(CustomCluster, LevelControl):
    """Override Level Control:
    1. Intercept write to current_level -> send move_to_level command
    2. Only expose current_level attribute (hide on_level etc.)
    """

    cluster_id = LevelControl.cluster_id  # 0x0008

    class AttributeDefs(BaseAttributeDefs):
        """Only expose current_level, hide all other Level Control attributes."""

        current_level: Final = ZCLAttributeDef(
            id=0x0000,
            type=t.uint8_t,
        )

    async def write_attributes(self, attributes, manufacturer=None):
        """Intercept write to current_level and send move_to_level command."""
        if "current_level" in attributes:
            level = int(attributes.pop("current_level"))
            await self.move_to_level(level=level, transition_time=0)
            # Update local cache so ZHA UI reflects the new value immediately
            self._attr_cache[self.AttributeDefs.current_level.id] = level
            return [[], []]
        return await super().write_attributes(attributes, manufacturer)


(
    QuirkBuilder("Third Reality, Inc", "3RAS1098Z")
    .replaces(SirenLevelControl)
    .number(
        cluster_id=SirenLevelControl.cluster_id,
        attribute_name="current_level",
        min_value=1,
        max_value=100,
        step=1,
        translation_key="current_song",
        fallback_name="Current song",
    )
    .add_to_registry()
)
