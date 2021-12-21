"""
Configuration package/module for microns-manual-proofreading.
"""
import datajoint.datajoint_plus as djp
from microns_utils.config_utils import SchemaConfig
from . import adapters
from . import externals

djp.enable_datajoint_flags()

minnie65_manual_proofreading_config = SchemaConfig(
    module_name='minnie65_manual_proofreading',
    schema_name='microns_minnie65_manual_proofreading',
    externals=externals.minnie65_manual_proofreading,
    adapters=adapters.minnie65_manual_proofreading
)

