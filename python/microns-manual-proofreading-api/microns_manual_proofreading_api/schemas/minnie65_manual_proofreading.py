"""
DataJoint tables for documenting manual proofreading in minnie65.
"""
import datajoint as dj
import datajoint.datajoint_plus as djp

from ..config import minnie65_manual_proofreading_config

minnie65_manual_proofreading_config.register_externals()
minnie65_manual_proofreading_config.register_adapters(context=locals())

schema = dj.schema(minnie65_manual_proofreading_config.schema_name, create_schema=True)
