"""
The npustat module.
"""

__version__ = "0.0.2"

from .cli import main, print_atlas_stat, loop_atlas_stat
from .core import AtlasCardCollection, AtlasCard
from .npu_smi import GetEntryCardListV1, GetCardStatusWithNpuSmi

__all__ = (
    "__version__",
    "AtlasCardCollection", "AtlasCard",
    "GetEntryCardListV1", "GetCardStatusWithNpuSmi",
    "main", "print_atlas_stat", "loop_atlas_stat",
)
