import json

from settings import *
from environment import *

# Either organize the imported methods by science app or by sensor
# Pull the relevant processing methods from the import
# and add to a common class that contains such methods as packaging,
# moving files, other common operations,
# and any operations that carry over all sensors
import TMprocessing
import ETMprocessing
# or maybe
# import LEDAPSprocessing


# Should come from the settings or environment import
TEMPLATE = 'template.json'


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
            if value:
                self.final_package.append(key[8:])

        # Should be wrapped in a try/except
        # sensor.get_methodlist should return an exception
        # if something is requested that is not supported
        self.required_methods = TMprocessing.get_methodlist(self.final_package)
        # or
        self.required_methods = ETMprocessing.get_methodlist(self.final_package)

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

        build_methods = self.required_methods
        build_methods['__init__'] = __init__

        return type(self.name, (ProcessClass,), build_methods)

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
        # Run the required methods in correct order
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
    debug = False
    json_order = 'some json order'
    processor = OrderLogic(json_order).get_processor()

    if debug:
        processor.debug_methods()
        processor.debug_attributes()
    else:
        processor.run()
