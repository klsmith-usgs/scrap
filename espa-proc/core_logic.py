import json
import os

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
    def __init__(self, jorder, local_debug=False):
        self.order_file = jorder

        with open(TEMPLATE, 'r') as f:
            self.jtemplate = json.load(f)

        with open(jorder) as f:
            self.jorder = json.load(f)

        # Determine which module to pull methods from
        # Or possibly multiple modules in cases of
        #  cross-sensor science products
        # self.sensor = self.jorder['product_type']
        self.name = 'name'  # order plus scene id?

        # Test objects to help in thinking about the problem
        self.final_package = []
        self.intermediate = []

        self.required_methods = {}
        self.proc_attributes = {}

        self.determine_requirements()
        self.determine_attributes()

        if local_debug:
            self.debug()

    def debug(self):
        print('\nInput JSON:\n{1}\n{0}'.format(json.dumps(self.jorder, sort_keys=True, indent=4),
                                               self.order_file))
        print('\nRequired Methods:\n{0}'.format(self.required_methods.keys()))
        print('\nAttributes Built:\n{0}'.format(json.dumps(self.proc_attributes, sort_keys=True, indent=4)))

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
        # Construct the attributes that will be built into
        # the processing class
        # most of which will be based on the settings and
        # environment imports, and the method list
        pass

    def class_factory(self):
        # Build the class that will do the processing
        # with the dictionary of the relevant methods
        # name = self.name

        def __init__(self, atts):
            # super(name, self).__init__()
            # ProcessClass.__init__(self)

            for key, value in atts.items():
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
        # self._type = classtype
        pass

    def run(self):
        # Place holder loop for visualization on run order
        # for proc in self.exec_order:
        #     self.proc()
        pass

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
    debug = True

    test_dir = r'D:\ESPA\scrap\espa-proc\test_jsons'
    for json_file in os.listdir(test_dir):
        if json_file[-4:] == 'json':
            json_order = os.path.join(test_dir, json_file)
            processor = OrderLogic(json_order, local_debug=True).get_processor()
            print processor.debug_methods()
            print processor.debug_attributes()
            # quit()

    # if debug:
    #     processor.debug_methods()
    #     processor.debug_attributes()
    # else:
    #     processor.run()
