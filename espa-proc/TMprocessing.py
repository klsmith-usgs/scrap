# This should be defined somewhere else and pulled in
VALID_INDICIES = ('sr_evi',
                  'sr_msavi',
                  'sr_nbr',
                  'sr_nbr2',
                  'sr_ndmi',
                  'sr_ndvi',
                  'sr_savi')

PROC_ORDER = ('source',
              'dem',
              'landwatermask',
              'ledaps',
              'indicies',
              'cfmask',
              'dswe',
              'emislst')


def get_methodlist(requested):
    # Return the methods to execute
    # based on the requested products
    # Should return an exception if there is
    # a bogus request
    out_methods = {}
    for prod in requested:
        rmethods = proc_list(prod)

        diff = list(set(out_methods.keys()).symmetric_difference(set(rmethods.keys())))
        for new in diff:
            out_methods[new] = rmethods[new]

    exec_order = []
    for proc in PROC_ORDER:
            if proc in out_methods.keys():
                exec_order.append(proc)

    return out_methods, tuple(exec_order)


def proc_source(self):
    print 'process source'


def proc_dem(self):
    print 'process dem'


def proc_landwatermask(self):
    print 'land water mask'


def proc_ledaps(self):
    print 'ledaps'


def proc_cfmask(self):
    print 'cfmask'


def proc_dswe(self):
    print 'dynamic surface water extent'


def proc_emislst(self):
    print 'land surface temperature'


def proc_sr_indicies(self):
    print 'spectral indicies'


def proc_statistics(self):
    print 'statistics'


def proc_list(prod):
    products = {'source_data': {'source': proc_source},
                'sr_toa': {'source': proc_source,
                           'ledaps': proc_ledaps},
                'sr': {'source': proc_source,
                       'landwatermask': proc_landwatermask,
                       'ledaps': proc_ledaps},
                'sr_indicies': {'source': proc_source,
                                'landwatermask': proc_landwatermask,
                                'ledaps': proc_ledaps,
                                'indicies': proc_sr_indicies},
                'cfmask': {'source': proc_source,
                           'ledaps': proc_ledaps,
                           'cfmask': proc_cfmask},
                'dswe': {'source': proc_source,
                         'dem': proc_dem,
                         'ledaps': proc_ledaps,
                         'cfmask': proc_cfmask,
                         'dswe': proc_dswe},
                'lst': {'source': proc_source,
                        'dem': proc_dem,
                        'landwatermask': proc_landwatermask,
                        'ledaps': proc_ledaps,
                        'emislst': proc_emislst}}

    if prod in products.keys():
        return products[prod]
    elif prod in VALID_INDICIES:
        return products['sr_indicies']
    else:
        return products['source_data']


# For visualization purposes, WiP
# source = {'source': proc_source}
#
# toa = {'source': proc_source,
#        'bt': proc_bt,
#        'toa': proc_toa}
#
# sr = {'source': proc_source,
#       'landwatermask': proc_landwatermask,
#       'toa': proc_toa,
#       'bt': proc_bt,
#       'sr': proc_sr}
#
# srindicies = {'source': proc_source,
#               'landwatermask': proc_landwatermask,
#               'toa': proc_toa,
#               'bt': proc_bt,
#               'sr': proc_sr,
#               'indicies': proc_sr_indicies}
#
# cfmask = {'source': proc_source,
#           'toa': proc_toa,
#           'bt': proc_bt,
#           'cfmask': proc_cfmask}
#
# dswe = {'source': proc_source,
#         'dem': proc_dem,
#         'toa': proc_toa,
#         'bt': proc_bt,
#         'sr': proc_sr,
#         'cfmask': cfmask,
#         'dswe': proc_dswe}
#
# emislst = {'source': proc_source,
#            'dem': proc_dem,
#            'landwatermask': proc_landwatermask,
#            'toa': proc_toa,
#            'bt': proc_bt,
#            'emislst': proc_emislst}
