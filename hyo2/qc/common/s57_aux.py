import logging
logger = logging.getLogger(__name__)


class S57Aux:
    """S57 selection methods"""

    @classmethod
    def filter_by_object(cls, objects, object_filter):
        """Return a new feature list filtered of the passed object filter"""
        new_list = list()
        for obj in objects:
            if obj.acronym in object_filter:
                continue
            new_list.append(obj)
        return new_list

    @classmethod
    def select_by_object(cls, objects, object_filter):
        """Return a new feature list with only the passed object filter"""
        new_list = list()
        for obj in objects:
            if obj.acronym in object_filter:
                new_list.append(obj)
        return new_list

    @classmethod
    def not_included_objects(cls, all_objects, sub_objects):
        """Return a new feature list with the object in all_objects not in sub_objects"""
        new_list = list()
        for obj in all_objects:
            found = False
            for sub_obj in sub_objects:
                if obj == sub_obj:
                    found = True
                    break
            if not found:
                new_list.append(obj)
        return new_list

    @classmethod
    def select_by_attribute(cls, objects, attribute):
        """Return a new feature list with only feature that have the passed attribute"""
        new_list = list()
        # logger.info("select by attribute \"%s\"" % attribute)
        for obj in objects:
            for attr in obj.attributes:
                # logger.info("%s" % attr.acronym)
                if attr.acronym == attribute:
                    new_list.append(obj)
                    continue
        return new_list

    @classmethod
    def filter_by_attribute(cls, objects, attribute):
        """Return a new feature list without feature that have the passed attribute"""
        new_list = list()
        # logger.info("filter by attribute \"%s\"" % attribute)
        for obj in objects:
            found = False

            for attr in obj.attributes:
                # logger.info("%s" % attr.acronym)
                if attr.acronym == attribute:
                    found = True
                    break
            if not found:
                new_list.append(obj)
        return new_list

    @classmethod
    def select_by_attribute_value(cls, objects: list, attribute: str, value_filter: list):
        """Return a new feature list with only feature that have the passed attribute values"""
        new_list = list()
        # logger.info("select by attribute \"%s\" if %s" % (attribute, value_filter))
        for obj in objects:
            for attr in obj.attributes:
                if (attr.acronym == attribute) and (attr.value in value_filter):
                    # logger.info("request: %s [%s] -> %s [%s]"
                    #             % (attribute, type(attribute), value_filter, type(value_filter)))
                    # logger.info("actual: %s [%s] -> %s [%s]"
                    #             % (attr.acronym, type(attr.acronym), attr.value, type(attr.value)))
                    new_list.append(obj)
                    continue
        return new_list

    @classmethod
    def filter_by_attribute_value(cls, objects, attribute, value_filter):
        """Return a new feature list without feature that have the passed attribute values"""
        new_list = list()
        # logger.info("filter by attribute \"%s\" if %s" % (attribute, value_filter))
        for obj in objects:
            found = False
            for attr in obj.attributes:
                # logger.info("%s: %s" % (attr.acronym, attr.value))
                if (attr.acronym == attribute) and (attr.value in value_filter):
                    found = True
                    break
            if not found:
                new_list.append(obj)
        return new_list

    @classmethod
    def select_by_attribute_float(cls, objects, attribute):
        """Return a new feature list with only feature that have a valid float value at the passed attribute"""
        new_list = list()
        # logger.info("select by attribute \"%s\" if %s" % (attribute, value_filter))
        for obj in objects:
            for attr in obj.attributes:
                # logger.info("%s: %s" % (attr.acronym, attr.value))
                if attr.acronym == attribute:
                    try:
                        _ = float(attr.value)
                        new_list.append(obj)
                    except ValueError:
                        pass
                    continue
        return new_list

    @classmethod
    def select_by_attribute_float_range(cls, objects, attribute, min_value, max_value):
        """Return a new feature list with only feature that have a float value in the passed validity range"""
        new_list = list()
        # logger.info("select by attribute \"%s\" if %s" % (attribute, value_filter))
        for obj in objects:
            for attr in obj.attributes:
                # logger.info("%s: %s" % (attr.acronym, attr.value))
                if attr.acronym == attribute:
                    try:
                        val = float(attr.value)
                        if (val >= min_value) and (val <= max_value):
                            # logger.debug("valid depth: %s" % val)
                            new_list.append(obj)
                    except ValueError:
                        pass
                    continue
        return new_list

    @classmethod
    def select_only_points(cls, objects):
        """Return a new feature list with only feature that have a single point as geometry"""
        new_list = list()
        for obj in objects:
            if len(obj.geo2s) == 1:
                new_list.append(obj)
            elif len(obj.geo3s) == 1:
                new_list.append(obj)
            else:
                continue
        return new_list

    @classmethod
    def select_lines_and_areas(cls, objects):
        """Return a new feature list with only feature that have line and area geometry"""
        new_list = list()
        for obj in objects:
            if len(obj.geo2s) > 1:
                new_list.append(obj)
            elif len(obj.geo3s) > 1:
                new_list.append(obj)
            else:
                continue
        return new_list
