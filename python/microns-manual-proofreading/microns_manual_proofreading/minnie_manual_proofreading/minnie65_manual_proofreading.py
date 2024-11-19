"""
Methods for filling DataJoint tables in minnie65_manual_proofreading.
"""

import datajoint_plus as djp
import pandas as pd
from pathlib import Path
import re 
from datetime import datetime
import microns_utils.ap_utils as apu
from microns_utils.datetime_utils import current_timestamp
from microns_manual_proofreading_api.schemas import minnie65_manual_proofreading as m65mprf

schema = m65mprf.schema
config = m65mprf.config

logger = djp.getLogger(__name__)


class Tag(m65mprf.Tag):
    pass


class ImportMethod(m65mprf.ImportMethod):
    @classmethod
    def run(cls, key):
        return cls.r1p(key).run(**key)

    class ExcelPrfSheet(m65mprf.ImportMethod.ExcelPrfSheet):
        def run(self, **kwargs):
            params = self.fetch1()
            if params['version'] == 1:
                csv_path = Path(params['path_to_csv'])
                if not csv_path.exists():
                    msg = f'csv file does not exist at path: {str(csv_path)}.'
                    self.Log('error', msg)
                    raise FileNotFoundError(msg)

                df = pd.read_csv(csv_path)
                df = df.rename(columns={'#': 'excel_id'})
                renamed_columns = [re.sub(r'\W+', '', s.lower().replace(' ', '_')).strip('_') for s in df.columns]
                df = df.rename(columns = {a: r for a, r in zip(df.columns, renamed_columns)})
                df = df.merge(df.nucleus_id.dropna(), how='right').drop_duplicates()
                df = df.loc[:, :'axon_in_white_matter']
                df = df.rename(columns={'proofreader': 'proofreader_den',
                                    'date_finished_den_ctrl': 'date_finished_den', 
                                        'notes':'notes_den',
                                        'notes1': 'notes_ax',
                                        'proofreader1': 'proofreader_ax',
                                    'date_finished_ax_ctrl': 'date_finished_ax', 'description': 'area'})
                df = df[[
                    'excel_id',
                    'nucleus_id', 
                    'area', 
                    'proofreader_den', 
                    'time_min_den', 
                    'notes_den', 
                    'finished_den', 
                    'date_finished_den', 
                    'proofreader_ax', 
                    'time_min_ax', 
                    'notes_ax', 
                    'finished_ax', 
                    'date_finished_ax', 
                    'axon_in_white_matter'
                ]]
                df.loc[:, 'finished_ax'] = df.finished_ax.apply(lambda x: 1*eval(x.title()))
                df.loc[:, 'finished_den'] = df.finished_den.apply(lambda x: 1*x)
                df.loc[:, 'axon_in_white_matter'] = df.axon_in_white_matter.apply(lambda x: 1*x)
                df.loc[:75, 'prf_method'] = PrfMethod.hash1({'prf_method_name': 'whole_cell'})
                df.loc[76:145, 'prf_method'] = PrfMethod.hash1({'prf_method_name': 'projection_only'})
                df.loc[146:, 'prf_method'] = PrfMethod.hash1({'prf_method_name': 'whole_cell'})
                df = df.query('finished_den == True and finished_ax == True')
                df = df.where(pd.notnull(df), None)
                df['ts_inserted'] = str(current_timestamp('US/Central'))
                df['import_method'] = params['import_method']
                return {'df': df}

    class CAVE(m65mprf.ImportMethod.CAVE, apu.CAVEClient):
        @classmethod
        def fill(cls, table_name, ver=None):
            """
            table_name (str) - name of CAVE table
            ver (int) - ver to pass to apu.CAVEClient; None --> latest
            """
            cls.set_client(ver=ver)
            assert table_name in cls.client.materialize.get_tables(), f'Table {table_name} not found in CAVEclient'
            cls.insert1({'table_name': table_name, 'ver': cls.client.materialize.version, 'tag': Tag.version}, insert_to_master=True)

        def run(self, **kwargs):
            params = self.fetch1()
            ver = int(params.get('ver'))
            assert Tag.version == params.get('tag'), 'Package version mismatch. Update Import Method.'
            self.set_client(ver=ver)
            assert self.client_ver == ver, f'Materialization version mismatch. Method requires {ver}. Client version: {self.client_ver}'
            nuc_df = self.client.materialize.query_table('nucleus_detection_v0')
            prf_status_df = self.client.materialize.query_table(params.get('table_name')).query('valid=="t"')
            merge_df = prf_status_df.merge(nuc_df, on='pt_root_id')
            df = merge_df.rename(columns=dict(id_y='nucleus_id'))[['nucleus_id', 'status_dendrite', 'status_axon']]
            df['import_method'] = params['import_method']
            return {'df': df}


class PrfMethod(m65mprf.PrfMethod):
    pass


class PrfNucleusSet(m65mprf.PrfNucleusSet):

    class ExcelPrfSheet(m65mprf.PrfNucleusSet.ExcelPrfSheet):
        pass

    class ExcelPrfSheetMaker(m65mprf.PrfNucleusSet.ExcelPrfSheetMaker):
        def make(self, key):
            df = ImportMethod.run(key)['df']
            df['prf_nuc_set'] = self.hash1(df, unique=True)
            self.master.ExcelPrfSheet.insert(df, ignore_extra_fields=True, insert_to_master=True, insert_to_master_kws={'ignore_extra_fields': True, 'skip_duplicates': True})
            self.insert(df, ignore_extra_fields=True, skip_hashing=True)
    
    class CAVEMaker(m65mprf.PrfNucleusSet.CAVEMaker):
        def make(self, key):
            df = ImportMethod.run(key)['df']
            df['prf_nuc_set'] = self.hash1(df, unique=True)
            self.master.CAVEProofreadingStatus.insert(df, ignore_extra_fields=True, skip_duplicates=True, insert_to_master=True, insert_to_master_kws={'ignore_extra_fields': True, 'skip_duplicates': True})
            self.insert(df, ignore_extra_fields=True, skip_duplicates=True, skip_hashing=True)

    class CAVEProofreadingStatus(m65mprf.PrfNucleusSet.CAVEProofreadingStatus):
        pass


class ExclusionMethod(m65mprf.ExclusionMethod):

    class Manual(m65mprf.ExclusionMethod.Manual):
        pass


class PrfNucleusExclude(m65mprf.PrfNucleusExclude):
    pass


class PrfNucleusReInclude(m65mprf.PrfNucleusReInclude):
    pass


class PrfNucleusIncludeSet(m65mprf.PrfNucleusIncludeSet):
    
    class Member(m65mprf.PrfNucleusIncludeSet.Member):

        @classmethod
        def fill(cls, prf_nuc_set_id):
            source = PrfNucleusSet.r1swh(prf_nuc_set_id)
            source -= (PrfNucleusExclude - PrfNucleusReInclude.proj())
            cls.insert(source, constant_attrs=dict(ts_computed=str(datetime.utcnow()), tag=Tag.version), ignore_extra_fields=True, skip_duplicates=True, insert_to_master=True)


class PrfNucleusIncludeSetRecommended(m65mprf.PrfNucleusIncludeSetRecommended):
    @classmethod
    def fill(cls, prf_nuc_include_set, description, replace=True):
        key = dict(
            prf_nuc_include_set=prf_nuc_include_set,
            description=description
        )
        cls.insert1(key, replace=replace)


class UnitSeedProtocol(m65mprf.UnitSeedProtocol):
    pass


class UnitSeedGroupMethod(m65mprf.UnitSeedGroupMethod):
    pass


class PrfNucSelectionInfo(m65mprf.PrfNucSelectionInfo):
    pass


class SpreadsheetLink(m65mprf.SpreadsheetLink):
    pass