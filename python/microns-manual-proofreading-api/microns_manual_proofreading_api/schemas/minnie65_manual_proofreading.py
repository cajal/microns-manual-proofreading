"""
DataJoint tables for documenting manual proofreading in minnie65.
"""

import datajoint_plus as djp
import datajoint as dj

from microns_materialization_api.schemas import minnie65_materialization as m65mat

from ..config import minnie65_manual_proofreading_config as config

config.register_externals()
config.register_adapters(context=locals())

schema = djp.schema(config.schema_name, create_schema=True)

@schema
class ImportMethod(djp.Lookup):
    hash_name = 'import_method'
    definition = """
    import_method : varchar(10) # import method hash
    """

    class ExcelPrfSheet(djp.Part):
        enable_hashing=True
        hash_name = 'import_method'
        hashed_attrs = 'version', 'path_to_csv'
        definition = """
        -> master
        ---
        version : int # method version
        path_to_csv : varchar(1000) # path to csv file
        """


@schema
class PrfMethod(djp.Lookup):
    enable_hashing = True
    hash_name = 'prf_method'
    hashed_attrs = 'prf_method_name'
    definition = """
    prf_method : varchar(6) # method of proofreading
    ---
    prf_method_name : varchar(48) # name of proofreading method
    prf_method_desc : varchar(1000) # proofreading description
    ts_inserted=CURRENT_TIMESTAMP : timestamp # timestamp inserted
    """
    contents = [{
        'prf_method_name': 'whole_cell',
        'prf_method_desc': 'all dendrites extended and cleaned, axon fully extended and cleaned'
        },
        {
        'prf_method_name': 'projection_only',
        'prf_method_desc': 'all dendrites extended and cleaned, only axon projection extended, axon cleaned.'
        }
    ]


@schema
class PrfNucleusSet(djp.Lookup):
    hash_name = 'prf_nuc_set'
    definition = """
    prf_nuc_set : varchar(12) # set hash
    """
    @classmethod
    def restrict_one_store(cls, part_restr={}, **kwargs):
        return cls.restrict_one_part_with_hash(part_restr=part_restr, include_parts=cls.ExcelPrfSheet, **kwargs)
    
    r1s = restrict_one_store

    @classmethod
    def restrict_one_maker(cls, part_restr={}, **kwargs):
        return cls.restrict_one_part_with_hash(part_restr, include_parts=cls.ExcelPrfSheetMaker, **kwargs)
    
    r1m = restrict_one_maker

    @classmethod
    def restrict_one_store_with_hash(cls, hash, **kwargs):
        return cls.restrict_one_part_with_hash(hash=hash, include_parts=cls.ExcelPrfSheet, **kwargs)
    
    r1swh = restrict_one_store_with_hash

    @classmethod
    def restrict_one_maker_with_hash(cls, hash, **kwargs):
        return cls.restrict_one_part_with_hash(hash=hash, include_parts=cls.ExcelPrfSheetMaker, **kwargs)
    
    r1mwh = restrict_one_maker_with_hash

    class ExcelPrfSheet(djp.Part):
        hash_name = 'prf_nuc_set'
        definition = """
        -> m65mat.Nucleus
        -> master
        ---
        excel_id : int # id of nucleus on excel sheet
        area : varchar(10) # visual area
        -> PrfMethod
        proofreader_den=NULL : varchar(450) # name of dendrite proofreader
        time_min_den=NULL : float # time to complete dendrites (min)
        notes_den=NULL : varchar(1000) # dendrites note
        finished_den : tinyint # dendrite finished (bool)
        date_finished_den=NULL : varchar(48) # date dendrite finished
        proofreader_ax=NULL : varchar(450) # name of axon proofreader
        time_min_ax=NULL : float # time to complete axon (min)
        notes_ax=NULL : varchar(1000) # axon notes 
        finished_ax : tinyint # axon finished (bool)
        date_finished_ax=NULL : varchar(48) # date axon finished
        axon_in_white_matter=NULL :  tinyint # 1 if axon passes into white matter (bool)
        """

    class ExcelPrfSheetMaker(djp.Part, dj.Computed):
        enable_hashing = True
        hash_name = 'prf_nuc_set'
        hashed_attrs = 'nucleus_id', 'import_method'
        hash_group = True
        definition = """
        -> master.ExcelPrfSheet
        -> ImportMethod
        ---
        ts_inserted : timestamp # timestamp inserted
        """

schema.spawn_missing_classes()
schema.connection.dependencies.load()