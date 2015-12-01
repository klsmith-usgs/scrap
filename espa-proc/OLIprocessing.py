from TMprocessing import VALID_INDICIES
from TMprocessing import proc_source
from TMprocessing import proc_cfmask
from TMprocessing import proc_dem
from TMprocessing import proc_dswe
from TMprocessing import proc_emislst
from TMprocessing import proc_landwatermask
from TMprocessing import proc_sr_indicies
from TMprocessing import get_methodlist


PROC_ORDER = ('source',
              'dem',
              'landwatermask',
              'l8sr',
              'indicies',
              'cfmask',
              'dswe',
              'emislst')


def proc_l8sr(self):
    print 'processing L8 SR'


def proc_list(prod):
    products = {'source_data': {'source': proc_source},
                'sr_toa': {'source': proc_source,
                           'ledaps': proc_l8sr},
                'sr': {'source': proc_source,
                       'landwatermask': proc_landwatermask,
                       'ledaps': proc_l8sr},
                'sr_indicies': {'source': proc_source,
                                'landwatermask': proc_landwatermask,
                                'ledaps': proc_l8sr,
                                'indicies': proc_sr_indicies},
                'cfmask': {'source': proc_source,
                           'ledaps': proc_l8sr,
                           'cfmask': proc_cfmask},
                'dswe': {'source': proc_source,
                         'dem': proc_dem,
                         'ledaps': proc_l8sr,
                         'cfmask': proc_cfmask,
                         'dswe': proc_dswe},
                'lst': {'source': proc_source,
                        'dem': proc_dem,
                        'landwatermask': proc_landwatermask,
                        'ledaps': proc_l8sr,
                        'emislst': proc_emislst}}

    if prod in products.keys():
        return products['prod']
    elif prod in VALID_INDICIES:
        return products['srindicies']
    else:
        # Should raise warning
        return products['source_data']
