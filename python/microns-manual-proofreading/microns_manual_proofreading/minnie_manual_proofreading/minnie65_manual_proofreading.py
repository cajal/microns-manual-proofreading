"""
Methods for filling DataJoint tables in minnie65_manual_proofreading.
"""

import datajoint_plus as djp
import pandas as pd
from pathlib import Path
import re 

from microns_utils.datetime_utils import current_timestamp_for_mysql
from microns_manual_proofreading_api.schemas import minnie65_manual_proofreading as m65mprf

schema = m65mprf.schema
config = m65mprf.config

logger = djp.getLogger(__name__)

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
                df.loc[:75, 'proofreading_method'] = 'whole_cell'
                df.loc[76:145, 'proofreading_method'] = 'projection_only'
                df.loc[146:, 'proofreading_method'] = 'whole_cell'
                df = df.query('finished_den == True and finished_ax == True')
                df = df.where(pd.notnull(df), None)
                df['ts_inserted'] = str(current_timestamp_for_mysql('US/Central'))
                df['import_method'] = params['import_method']
                return {'df': df}


class PrfNucleusSet(m65mprf.PrfNucleusSet):

    class ExcelPrfSheet(m65mprf.PrfNucleusSet.ExcelPrfSheet):
        pass

    class ExcelPrfSheetMaker(m65mprf.PrfNucleusSet.ExcelPrfSheetMaker):
        @property
        def key_source(self):
            return ImportMethod.ExcelPrfSheet

        def make(self, key):
            df = ImportMethod.run(key)['df']
            df['prf_nuc_set'] = self.hash1(df, unique=True)
            self.master.ExcelPrfSheet.insert(df, ignore_extra_fields=True, insert_to_master=True, insert_to_master_kws={'ignore_extra_fields': True, 'skip_duplicates': True})
            self.insert(df, ignore_extra_fields=True, skip_hashing=True)