import json

from settings import *
from environment import *

# Either organize the imported methods by sensor
# Pull the relevant processing methods from the import
# and add to a common class that contains such methods as packaging,
# moving files, other common operations,
# and any operations that carry over all sensors
import TMprocessing
import ETMprocessing
import OLIprocessing


imports = {'TM': TMprocessing,
           'ETM': ETMprocessing,
           'OLI': OLIprocessing}

# Should come from the settings or environment import
TEMPLATE = 'template.json'

# Just for testing purposes, also allows for things to be
# added serially and taken off the list
TEMP_UNSUPPORTED_INCLUDES = ('customized_source_data',
                             'solr_index',
                             'source_data_metadata',
                             'sr_browse',
                             'sr_thermal',
                             'statistics')


class OrderLogic(object):
    # Build a list of operations that are needed to carry out
    # Bonus provide the methods with the information built in
    def __init__(self, json_order):
        with open(TEMPLATE, 'r') as f:
            self.jtemplate = json.load(f)

        self.jorder = json.load(json_order)

        # Determine which module to pull methods from
        # Or possibly multiple modules in cases of
        #  cross-sensor science products
        self.sensor = self.jorder['product_type']

        self.name = 'name'  # order plus scene id?

        # Test objects to help in thinking about the problem
        self.final_package = []
        self.intermediate = []

        self.required_methods = {}
        self.proc_attributes = {}

        self.determine_attributes()

    def verify_order(self):
        # Verify the dictionary keys in jorder match jtemplate
        # Possibly determine the differences to return an Exception
        # Or determine what processes are needed
        # using a modified:
        # https://github.com/hughdbrown/dictdiffer
        pass

    def determine_requirements(self):
        # Get the steps required for requested product

        # Determine what processes need to happen

        for key, value in self.jorder['options'].items():
            if value and key[8:] not in TEMP_UNSUPPORTED_INCLUDES:
                self.final_package.append(key[8:])

        try:
            self.required_methods, self.proc_attributes['exec_order'] = imports['TM'].get_methodlist(self.final_package)
        except Exception:
            raise

    def determine_attributes(self):
        # Contruct the attributes that will be built into
        # the processing class
        # most of which will be based on the settings and
        # environment imports, and the method list
        pass

    def class_factory(self):
        # Build the class that will do the processing
        # with the dictionary of the relevant methods
        def __init__(self, **kwargs):
            super(self.__name__, self).__init__(**kwargs)

            for key, value in kwargs.items():
                setattr(self, key, value)

        self.required_methods['__init__'] = __init__

        return type(self.name, (ProcessClass,), self.required_methods)

    def get_processor(self):
        newclass = self.class_factory()
        return newclass(self.proc_attributes)


class ProcessClass(object):
    """
    Contains the common base processing methods
    """
    def __init__(self):
        pass

    def run(self):
        # Place holder loop
        for proc in self.exec_order:
            self.proc()

    def debug_methods(self):
        # Return the methods and attributes
        return dir(self)

    def debug_attributes(self):
        # Return the attributes and their values
        return vars(self)

    def package(self):
        print 'packaging'

    def working_cleanup(self):
        print 'cleaning up'

    def customize(self):
        print 'customizing output'


if __name__ == '__main__':
    debug = False
    json_order = 'some json order'
    processor = OrderLogic(json_order).get_processor()

    if debug:
        processor.debug_methods()
        processor.debug_attributes()
    else:
        processor.run()
