# Ideally each sensor has it's own processing module that gets imported

def get_methodlist(requested):
    # Return an ordered list of methods to execute
    # based on the requested products
    # Should return an exception if there is
    # a bogus request
    pass


def proc_source(self):
    print 'process source'


def proc_dem(self):
    print 'process dem'


def proc_landwatermask(self):
    print 'land water mask'


def proc_toa(self):
    print 'top of atmosphere'


def proc_bt(self):
    print 'brightness temperature'


def proc_sr(self):
    print 'surface reflectance'


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


# For visualization purposes, WiP
source = {'source': proc_source}

toa = {'source': proc_source,
       'bt': proc_bt,
       'toa': proc_toa}

sr = {'source': proc_source,
      'landwatermask': proc_landwatermask,
      'toa': proc_toa,
      'bt': proc_bt,
      'sr': proc_sr}

srindicies = {'source': proc_source,
              'landwatermask': proc_landwatermask,
              'toa': proc_toa,
              'bt': proc_bt,
              'sr': proc_sr,
              'indicies': proc_sr_indicies}

cfmask = {'source': proc_source,
          'toa': proc_toa,
          'bt': proc_bt,
          'cfmask': proc_cfmask}

dswe = {'source': proc_source,
        'dem': proc_dem,
        'toa': proc_toa,
        'bt': proc_bt,
        'sr': proc_sr,
        'cfmask': cfmask,
        'dswe': proc_dswe}

emislst = {'source': proc_source,
           'dem': proc_dem,
           'landwatermask': proc_landwatermask,
           'toa': proc_toa,
           'bt': proc_bt,
           'emislst': proc_emislst}
