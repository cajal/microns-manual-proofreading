"""
DataJoint tables for documenting manual proofreading in minnie65.
"""

import datajoint_plus as djp
import datajoint as dj

import microns_utils.datajoint_utils as dju
from microns_utils.misc_utils import classproperty
from microns_materialization_api.schemas import minnie65_materialization as m65mat

from ..config import minnie65_manual_proofreading_config as config

config.register_externals()
config.register_adapters(context=locals())

schema = djp.schema(config.schema_name, create_schema=True)


@schema
class Tag(dju.VersionLookup):
    package = 'microns-manual-proofreading-api'
    attr_name = 'tag'


@schema
class ImportMethod(djp.Lookup):
    hash_name = 'import_method'
    definition = """
    import_method : varchar(10) # import method hash
    """

    class ExcelPrfSheet(djp.Part):
        enable_hashing = True
        hash_name = 'import_method'
        hashed_attrs = 'version', 'path_to_csv'
        definition = """
        -> master
        ---
        version : int # method version
        path_to_csv : varchar(1000) # path to csv file
        """

    class CAVE(djp.Part):
        enable_hashing = True
        hash_name = 'import_method'
        hashed_attrs = 'table_name', 'tag', 'ver'
        definition  = """
        -> master
        ---
        table_name : varchar(128)
        -> m65mat.Materialization
        -> Tag
        ts_inserted=CURRENT_TIMESTAMP : timestamp
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
    @classproperty
    def makers(cls):
        return [cls.ExcelPrfSheetMaker, cls.CAVEMaker]

    @classproperty
    def stores(cls):
        return [cls.ExcelPrfSheet, cls.CAVEProofreadingStatus]

    @classmethod
    def restrict_one_maker(cls, part_restr={}, **kwargs):
        kwargs.setdefault('include_parts', cls.makers)
        return cls.restrict_one_part(part_restr, **kwargs)
    
    @classmethod
    def restrict_one_store(cls, part_restr={}, **kwargs):
        kwargs.setdefault('include_parts', cls.stores)
        return cls.restrict_one_part(part_restr=part_restr, **kwargs)
    
    @classmethod
    def restrict_one_maker_with_hash(cls, hash, **kwargs):
        kwargs.setdefault('include_parts', cls.makers)
        return cls.restrict_one_part_with_hash(hash=hash, **kwargs)
    
    @classmethod
    def restrict_one_store_with_hash(cls, hash, **kwargs):
        kwargs.setdefault('include_parts', cls.stores)
        return cls.restrict_one_part_with_hash(hash=hash, **kwargs)

    r1m = restrict_one_maker
    r1s = restrict_one_store    
    r1mwh = restrict_one_maker_with_hash
    r1swh = restrict_one_store_with_hash

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
        @classproperty
        def key_source(self):
            return ImportMethod.ExcelPrfSheet

    class CAVEMaker(djp.Part, dj.Computed):
        enable_hashing = True
        hash_name = 'prf_nuc_set'
        hashed_attrs = 'import_method'
        hash_group = True
        definition = """
        -> master
        -> ImportMethod
        ---
        ts_inserted=CURRENT_TIMESTAMP : timestamp # timestamp inserted
        """

        @classproperty
        def key_source(cls):
            return ImportMethod.CAVE

    class CAVEProofreadingStatus(djp.Part):
        hash_name = 'prf_nuc_set'
        definition = """
        -> m65mat.Nucleus
        -> master
        ---
        status_dendrite : varchar(450) # dendrite proofreading status
        status_axon : varchar(450) # axon proofreading status
        """


@schema
class ExclusionMethod(djp.Lookup):
    hash_name = 'exclusion_method_id'
    definition = """
    exclusion_method_id : varchar(8) # id of exclusion method
    """

    class Manual(djp.Part):
        enable_hashing = True
        insert_to_master = True
        hash_name = 'exclusion_method_id'
        hashed_attrs = 'exclusion_method_name', 'exclusion_method_desc'
        definition = """
        -> master
        ---
        exclusion_method_name : varchar(32)
        exclusion_method_desc=NULL : varchar(1000)
        exclusion_method_ts=CURRENT_TIMESTAMP : timestamp
        """

        @classmethod
        def update_method(cls, exclusion_method_name, exclusion_method_desc=None):
            d = {'exclusion_method_name': exclusion_method_name}
            if exclusion_method_desc is not None:
                d['exclusion_method_desc'] = exclusion_method_desc
            cls.insert1(d, insert_to_master=True)


@schema
class PrfNucleusExclude(djp.Lookup):
    definition = """
    -> ExclusionMethod
    nucleus_id           : int unsigned                 # id of segmented nucleus.
    ---
    exclude_user_id              : varchar(64)          # User performing exclusion
    ts_inserted=CURRENT_TIMESTAMP : timestamp           #
    """

    @classmethod
    def exclude(cls, key, exclusion_method_id, exclude_user_id):
        constant_attrs = dict(
            exclusion_method_id=exclusion_method_id,
            exclude_user_id=exclude_user_id
        )
        cls.insert1(
            key, 
            constant_attrs=constant_attrs, 
            allow_direct_insert=True, 
            skip_duplicates=True
        )


@schema
class PrfNucleusReInclude(djp.Lookup):
    definition = """
    nucleus_id           : int unsigned                 # id of segmented nucleus.
    ---
    description=NULL : varchar(1000) # description of reinclusion
    reinclude_user_id              : varchar(64)          # User performing reinclusion
    ts_inserted=CURRENT_TIMESTAMP : timestamp           #
    """

    @classmethod
    def reinclude(cls, key, reinclude_user_id, description=None):
        constant_attrs = dict(
            reinclude_user_id=reinclude_user_id,
            description=description
        )
        cls.insert1(
            key, 
            constant_attrs=constant_attrs, 
            allow_direct_insert=True, 
            skip_duplicates=True
        )


@schema
class PrfNucleusIncludeSet(djp.Lookup):
    hash_name = 'prf_nuc_include_set'
    definition = f"""
    {hash_name} : varchar(6) # proofread nucleus include set id
    """
    
    class Member(djp.Part):
        enable_hashing = True
        hash_name = 'prf_nuc_include_set'
        hashed_attrs = 'nucleus_id', 'prf_method', 'ts_computed'
        hash_group = True
        definition = """
        -> master
        nucleus_id           : int unsigned                 # id of segmented nucleus.
        ts_computed : timestamp
        ---
        -> PrfMethod
        area                 : varchar(10)                  # visual area
        -> Tag
        """


@schema
class PrfNucleusIncludeSetRecommended(djp.Lookup):
    definition = """
    -> PrfNucleusIncludeSet
    ---
    description : varchar(1000) # description of recommended include set
    timestamp=CURRENT_TIMESTAMP : timestamp
    """


@schema
class UnitSeedProtocol(djp.Lookup):
    definition = """
    # imported from microns_minnie65_02.UnitSeedProtocol
    protocol_id          : tinyint                      # id of protocol
    ---
    protocol_name        : varchar(256)                 # name of protocol
    cylinder_x=null      : float                        # x position of cylinder
    cylinder_y=null      : float                        # y position of cylinder
    cylinder_r=null      : float                        # radius of cylinder
    xmin=null            : float                        # xmin
    xmax=null            : float                        # xmax
    ymin=null            : float                        # ymin
    ymax=null            : float                        # ymax
    zmin=null            : float                        # zmin
    zmax=null            : float                        # zmax
    oracle_min=null      : float                        # minimum unit oracle pearson correlation over all movies
    test_corr_min=null   : double                       # minimum corr(dynamic model, trial response) for each unit (model test correlation)
    mean_corr_min=null   : double                       # minimum corr(dynamic model, mean response) for each unit (new fraction of oracle)
    real_von_pred_adv_min=null : float                        # mouse von mises predictive advantage over shuffled data
    model_von_pred_adv_min=null : float                        # model von mises predictive advantage over shuffled data
    description          : varchar(256)                 # protocol description
    brain_areas=null     : varchar(45)                  # 
    """
    

@schema
class UnitSeedGroupMethod(djp.Lookup):
    definition = """
    # Selection method for candidate functional units for proofreading
    group_method_id      : int                          # id for method of grouping seed cells from the seed candidates
    ---
    description          : varchar(256)                 # description for method of grouping seed cells
    """


@schema
class PrfNucSelectionInfo(djp.Lookup):
    definition = """
    # Unit seed protocol and group method for proofread nuclei
    nucleus_id : int unsigned # id of segmented nucleus
    ---
    -> UnitSeedProtocol
    -> UnitSeedGroupMethod
    source : varchar(256)
    notes=NULL : varchar(1000)
    timestamp=CURRENT_TIMESTAMP : timestamp
    """

@schema
class SpreadsheetLink(djp.Lookup):
    definition = """
    spreadsheet_name : varchar(256) # name of spreadsheet
    ---
    spreadsheet_link : varchar(1000)
    description : varchar(1000)
    timestamp=CURRENT_TIMESTAMP : timestamp
    """