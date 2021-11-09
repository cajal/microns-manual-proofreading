"""
Configuration package/module for microns-coregistration.
"""

from . import adapters
from . import externals

import traceback

try:
    import datajoint as dj
except:
    traceback.print_exc()
    raise ImportError('DataJoint package not found.')

from enum import Enum

import microns_utils
    
microns_utils.enable_datajoint_flags()

def register_externals(schema_name:str):
    """
    Registers the external stores for a schema_name in this module.
    """
    return microns_utils.register_adapters(schema_name=schema_name, externals_mapping=externals_mapping)


def register_adapters(schema_name:str, context=None):
    """
    Imports the adapters for a schema_name into the global namespace.
    """
    return microns_utils.register_adapters(schema_name=schema_name, adapters_mapping=adapters_mapping, context=context)


def create_vm(schema_name:str):
    """
    Creates a virtual module after registering the external stores, and includes the adapter objects in the vm.
    """
    return microns_utils.create_vm(schema_name=schema_name, externals_mapping=externals_mapping, adapters_mapping=adapters_mapping)


class SCHEMAS(Enum):
    MINNIE65_MANUAL_PROOFREADING = 'microns_minnie65_manual_proofreading'


config_mapping = {
    SCHEMAS.MINNIE65_MANUAL_PROOFREADING: {
        "externals": None,
        "adapters": None
    }
}

adapters_mapping = {SCHEMA.name: config_mapping[SCHEMA]['adapters'] for SCHEMA in SCHEMAS}

externals_mapping = {SCHEMA.name: config_mapping[SCHEMA]['externals'] for SCHEMA in SCHEMAS}