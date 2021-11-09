import datajoint as dj
from datajoint import datajoint_plus as djp

import numpy as np
import pandas as pd

import microns_nda_config as config
schema_name = 'microns_minnie65_manual_proofreading'

config.register_adapters(schema_name, context=locals())
config.register_externals(schema_name)

schema = dj.schema(schema_name)
schema.spawn_missing_classes()