from osgeo import ogr
import os
import logging

from hyo2.abc.lib.gdal_aux import GdalAux
from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)


class ShpWriter:

    @classmethod
    def _create_ogr_point_lyr_and_fields(cls, ds):
        # create the only data layer
        lyr = ds.CreateLayer('qctools', None, ogr.wkbPoint25D)
        if lyr is None:
            logger.error("Layer creation failed")
            return

        field = ogr.FieldDefn('info', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('note', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        return lyr

    @classmethod
    def _create_ogr_line_lyr_and_fields(cls, ds):
        # create the only data layer
        lyr = ds.CreateLayer('qctools', None, ogr.wkbLineString)
        if lyr is None:
            logger.error("Layer creation failed")
            return

        field = ogr.FieldDefn('info', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('note', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        return lyr

    @classmethod
    def write_soundings(cls, feature_list, path):
        """Feature list as list of long, lat, depth"""
        if not os.path.exists(os.path.dirname(path)):
            raise RuntimeError("the passed path does not exist: %s" % path)

        path = Helper.truncate_too_long(path)

        if not isinstance(feature_list, list):
            raise RuntimeError("the passed parameter as feature_list is not a list: %s" % type(feature_list))

        if os.path.splitext(path)[-1] == '.shp':
            path = path[:-4]

        GdalAux()
        # create the data source
        try:
            ds = GdalAux.create_ogr_data_source(ogr_format=GdalAux.ogr_formats['ESRI Shapefile'],
                                                output_path=path)
            lyr = cls._create_ogr_point_lyr_and_fields(ds)

        except RuntimeError as e:
            logger.error("%s" % e)
            return

        for feature in feature_list:
            ft = ogr.Feature(lyr.GetLayerDefn())
            ft.SetField('info', "%.1f" % feature[2])

            pt = ogr.Geometry(ogr.wkbPoint25D)
            pt.SetPoint(0, feature[0], feature[1], feature[2])

            try:
                ft.SetGeometry(pt)

            except Exception as e:
                RuntimeError("%s > pt: %s, %s, %s" % (e, feature[0], feature[1], feature[2]))

            if lyr.CreateFeature(ft) != 0:
                raise RuntimeError("Unable to create feature")
            ft.Destroy()

        return True

    @classmethod
    def write_bluenotes(cls, feature_list, path, list_of_list=True):
        if not os.path.exists(os.path.dirname(path)):
            raise RuntimeError("the passed path does not exist: %s" % path)

        path = Helper.truncate_too_long(path)

        if not isinstance(feature_list, list):
            raise RuntimeError("the passed parameter as feature_list is not a list: %s" % type(feature_list))

        if os.path.splitext(path)[-1] == '.shp':
            path = path[:-4]

        GdalAux()
        # create the data source
        try:
            ds = GdalAux.create_ogr_data_source(ogr_format=GdalAux.ogr_formats['ESRI Shapefile'],
                                                output_path=path)
            lyr = cls._create_ogr_point_lyr_and_fields(ds)

        except RuntimeError as e:
            logger.error("%s" % e)
            return

        if list_of_list:
            if len(feature_list[0]) != len(feature_list[1]):
                raise RuntimeError("invalid input for list of list")
            tmp_list = feature_list
            feature_list = list()
            for i, x in enumerate(tmp_list[0]):
                feature_list.append([x, tmp_list[1][i], tmp_list[2][i]])

        for feature in feature_list:
            ft = ogr.Feature(lyr.GetLayerDefn())
            ft.SetField('note', feature[2])

            pt = ogr.Geometry(ogr.wkbPoint25D)
            pt.SetPoint(0, feature[0], feature[1])

            try:
                ft.SetGeometry(pt)

            except Exception as e:
                RuntimeError("%s > pt: %s, %s" % (e, feature[0], feature[1]))

            if lyr.CreateFeature(ft) != 0:
                raise RuntimeError("Unable to create feature")
            ft.Destroy()

        return True

    @classmethod
    def write_tin(cls, feature_list_a, feature_list_b, path, list_of_list=True):
        if not os.path.exists(os.path.dirname(path)):
            raise RuntimeError("the passed path does not exist: %s" % path)

        path = Helper.truncate_too_long(path)

        if not isinstance(feature_list_a, list):
            raise RuntimeError("the passed parameter as feature_list_a is not a list: %s" % type(feature_list_a))

        if not isinstance(feature_list_b, list):
            raise RuntimeError("the passed parameter as feature_list_b is not a list: %s" % type(feature_list_b))

        if os.path.splitext(path)[-1] == '.shp':
            path = path[:-4]

        GdalAux()
        # create the data source
        try:
            ds = GdalAux.create_ogr_data_source(ogr_format=GdalAux.ogr_formats['ESRI Shapefile'],
                                                output_path=path)
            lyr = cls._create_ogr_line_lyr_and_fields(ds)

        except RuntimeError as e:
            logger.error("%s" % e)
            return

        if list_of_list:
            if len(feature_list_a[0]) != len(feature_list_a[1]):
                raise RuntimeError("invalid input for list of list")
            if len(feature_list_b[0]) != len(feature_list_b[1]):
                raise RuntimeError("invalid input for list of list")
            if len(feature_list_a) != len(feature_list_b):
                raise RuntimeError("invalid input for list of list")

            tmp_list_a = feature_list_a
            feature_list_a = list()
            for i, x in enumerate(tmp_list_a[0]):
                feature_list_a.append([x, tmp_list_a[1][i]])

            tmp_list_b = feature_list_b
            feature_list_b = list()
            for i, x in enumerate(tmp_list_b[0]):
                feature_list_b.append([x, tmp_list_b[1][i]])

        for i, point in enumerate(feature_list_a):
            ft = ogr.Feature(lyr.GetLayerDefn())
            ft.SetField('note', "tin edge")

            ln = ogr.Geometry(ogr.wkbLineString)
            ln.AddPoint(point[0], point[1])
            ln.AddPoint(feature_list_b[i][0], feature_list_b[i][1])

            try:
                ft.SetGeometry(ln)

            except Exception as e:
                RuntimeError("%s > ln: %s, %s / %s, %s"
                             % (e, point[0], point[1], feature_list_b[i][0], feature_list_b[i][1]))

            if lyr.CreateFeature(ft) != 0:
                raise RuntimeError("Unable to create feature")
            ft.Destroy()

        return True
