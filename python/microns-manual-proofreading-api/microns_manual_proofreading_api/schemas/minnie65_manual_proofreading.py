"""
DataJoint tables for documenting manual proofreading in minnie65.
"""
import datajoint as dj
import datajoint.datajoint_plus as djp

from ..config import minnie65_manual_proofreading_config as config

config.register_externals()
config.register_adapters(context=locals())

schema = dj.schema(config.schema_name, create_schema=True)
