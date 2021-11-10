import datajoint as dj
from datajoint import datajoint_plus as djp

import numpy as np
import pandas as pd

from microns_manual_proofreading_api import config
schema_obj = config.SCHEMAS.MINNIE65_MANUAL_PROOFREADING

config.register_adapters(schema_obj, context=locals())
config.register_externals(schema_obj)

schema = dj.schema(schema_obj.value)
schema.spawn_missing_classes()