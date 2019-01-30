import ogr
import os
import shutil
import piexif
from PIL import Image
import logging

from hyo2.qc.survey.sbdare.base_sbdare import BaseSbdare, sbdare_algos, s57_to_cmecs
from hyo2.qc.common.s57_aux import S57Aux
from hyo2.qc.common.geodesy import Geodesy
from hyo2.abc.lib.gdal_aux import GdalAux

logger = logging.getLogger(__name__)


class SbdareInfo:

    def __init__(self):

        self.observed_time = str()
        self.colour = str()
        self.natqua = str()
        self.natsur = str()
        self.remrks = str()
        self.sordat = str()
        self.sorind = str()

        self.images = str()
        self.image1 = str()
        self.image2 = str()
        self.image3 = str()
        self.image4 = str()

        self.c_subn = str()
        self.c_subc = str()
        self.c_cen1 = str()
        self.c_cec1 = str()
        self.c_cen2 = str()
        self.c_cec2 = str()

        self.natqua_list = list()
        self.natsur_list = list()
        self.images_list = list()


class SbdareExportV4(BaseSbdare):

    def __init__(self, s57, s57_path, do_exif=False, images_folder=None):
        super().__init__(s57=s57)
        self.s57_path = s57_path
        self.do_exif = do_exif
        self.images_folder = images_folder
        self._check_images_folder()
        self.type = sbdare_algos["SBDARE_EXPORT_v4"]
        self.all_features = self.s57.rec10s
        self.sbdare_features = list()

        self.flagged_natsur = list()
        self.flagged_colour = list()

        self.output_ascii = None
        self.cmecs_output_folder = None
        self.output_shp = None
        self.images_output_folder = None

        self.has_images = False

    def _check_images_folder(self):
        if self.images_folder is not None:
            logger.debug("images folder: %s" % self.images_folder)
            return

        input_folder = os.path.dirname(self.s57_path)
        # logger.debug("input folder: %s" % input_folder)

        multimedia_folder = os.path.join(input_folder, "Multimedia")
        if not os.path.exists(multimedia_folder):
            wrn = "The input images folder was not found."
            self.warnings.append(wrn)
            logger.debug(wrn)
            return

        self.images_folder = multimedia_folder
        logger.debug("images folder: %s" % self.images_folder)

    def has_sbdare_issues(self):
        """Return true is there are issues with sbdare attributes"""

        natsur_flagged = len(self.flagged_natsur) > 0
        colour_flagged = len(self.flagged_colour) > 0
        return natsur_flagged or colour_flagged

    def run(self):
        """Execute the set of check of the SBDARE check algorithm"""

        self.sbdare_features = S57Aux.select_by_object(self.all_features, object_filter=['SBDARE', ])
        self.sbdare_features = S57Aux.select_only_points(self.sbdare_features)

        logger.debug("identified %d SBDARE features" % len(self.sbdare_features))

    def generate_output(self, output_folder, output_name):

        logger.debug("do EXIF: %s" % self.do_exif)

        # create ascii file
        self.output_ascii = os.path.join(output_folder, "%s.ascii" % output_name)
        ascii_fod = open(self.output_ascii, 'w')
        ascii_fod.write('Latitude;Longitude;Observed time;Colour;Nature of surface - qualifying terms;'
                        'Nature of surface;Remarks;Source date;Source indication;Images;'
                        'CMECS Substrate Name;CMECS Substrate Code;'
                        'CMECS Co-occurring Element 1 Name;CMECS Co-occurring Element 1 Code;'
                        'CMECS Co-occurring Element 2 Name;CMECS Co-occurring Element 2 Code\n')

        # create output folder
        self.cmecs_output_folder = os.path.join(output_folder, output_name)
        if not os.path.exists(self.cmecs_output_folder):
            os.mkdir(self.cmecs_output_folder)

        # create 'Images' output folder
        self.images_output_folder = os.path.join(self.cmecs_output_folder, "Images")
        if not os.path.exists(self.images_output_folder):
            os.mkdir(self.images_output_folder)

        # create shapefile
        self.output_shp = os.path.join(self.cmecs_output_folder, output_name)
        GdalAux()
        try:
            ds = GdalAux.create_ogr_data_source(ogr_format=GdalAux.ogr_formats['ESRI Shapefile'],
                                                output_path=self.output_shp)
            lyr = self._create_ogr_point_lyr_and_fields(ds)

        except RuntimeError as e:
            logger.error("%s" % e)
            return False

        # populate
        for idx, feature in enumerate(self.sbdare_features):

            # create OGR feature
            ft = ogr.Feature(lyr.GetLayerDefn())

            # retrieve position for ASCII format
            lat = Geodesy.dd2dms(feature.centroid.y)
            lon = Geodesy.dd2dms(feature.centroid.x)
            lat_str = "%02.0f-%02.0f-%05.2f%s" % (abs(lat[0]), lat[1], lat[2], ("N" if (lat[0] > 0) else "S"))
            lon_str = "%03.0f-%02.0f-%05.2f%s" % (abs(lon[0]), lon[1], lon[2], ("E" if (lon[0] > 0) else "W"))
            # print(lat_str, lon_str)

            # retrieve position for shapefile format
            pt = ogr.Geometry(ogr.wkbPoint)
            pt.SetPoint(0, feature.centroid.x, feature.centroid.y)
            try:
                ft.SetGeometry(pt)
            except Exception as e:
                RuntimeError("%s > #%d pt: %s, %s" % (e, idx, feature.centroid.x, feature.centroid.y))

            info = self._retrieve_info(feature=feature, feature_idx=idx)
            info = self._calc_cmecs(info=info, feature_idx=idx)

            # for each SBDARE, write a row in the ASCII file
            ascii_fod.write("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n"
                            % (lat_str, lon_str,
                               info.observed_time, info.colour, info.natqua, info.natsur,
                               info.remrks, info.sordat, info.sorind,
                               info.images, info.c_subn, info.c_subc,
                               info.c_cen1, info.c_cec1, info.c_cen2, info.c_cec2))

            # actually write the feature in the shapefile
            self._write_shape_attributes(ft, info)
            if lyr.CreateFeature(ft) != 0:
                raise RuntimeError("Unable to create feature")
            ft.Destroy()

        # finalize ASCII file
        ascii_fod.close()

        return self._finalize_generate_output(root_folder=output_folder, base_folder=output_name, remove_folder=False)

    @classmethod
    def _zeroed_list(cls, str_list):
        str_out = str()

        last_idx = len(str_list) - 1
        for idx, item in enumerate(str_list):
            if item == "":
                item = "0"

            str_out += item

            if idx != last_idx:
                str_out += ","

        return str_out

    @classmethod
    def _commaed_str(cls, input_str):
        str_out = str()

        str_list = input_str.strip().splitlines()
        # logger.debug("str list : %s" % (str_list, ))
        last_idx = len(str_list) - 1
        for idx, item in enumerate(str_list):

            str_out += item
            if idx != last_idx:
                str_out += ","

        return str_out

    @classmethod
    def _semi_commaed_str(cls, input_str):
        str_out = str()

        str_list = input_str.strip().splitlines()
        # logger.debug("str list : %s" % (str_list, ))
        last_idx = len(str_list) - 1
        for idx, item in enumerate(str_list):

            str_out += item
            if idx != last_idx:
                str_out += ";"

        return str_out

    def _retrieve_info(self, feature, feature_idx):
        info = SbdareInfo()

        # retrieve attribute information

        for attribute in feature.attributes:

            if attribute.acronym == 'obstim':
                info.observed_time = attribute.value.strip()

            elif attribute.acronym == 'COLOUR':
                info.colour = self._commaed_str(attribute.value)

            elif attribute.acronym == 'NATQUA':
                info.natqua = self._commaed_str(attribute.value)
                info.natqua_list = info.natqua.split(",")

            elif attribute.acronym == 'NATSUR':
                info.natsur = self._commaed_str(attribute.value)
                info.natsur_list = info.natsur.split(",")

            elif attribute.acronym == 'remrks':
                info.remrks = self._commaed_str(attribute.value)

            elif attribute.acronym == 'SORDAT':
                info.sordat = attribute.value.strip()

            elif attribute.acronym == 'SORIND':
                info.sorind = attribute.value.strip()

            elif attribute.acronym == 'images':
                info.images = self._commaed_str(attribute.value.replace(";", ","))
                info.images_list = info.images.split(",")
                if len(info.images_list) > 0:
                    self.has_images = True

                for img_idx, img in enumerate(info.images_list):

                    if img_idx == 0:
                        info.image1 = img
                    elif img_idx == 1:
                        info.image2 = img
                    elif img_idx == 2:
                        info.image3 = img
                    elif img_idx == 3:
                        info.image4 = img

                    self._check_image(feature=feature, feature_idx=feature_idx, img=img)

            info.natqua = self._zeroed_list(info.natqua_list)
            info.natqua_list = info.natqua.split(",")
            info.natsur = self._zeroed_list(info.natsur_list)
            info.natsur_list = info.natsur.split(",")

        return info

    def _check_image(self, feature, feature_idx, img):

        if self.images_folder is None:
            wrn = "Unable to locate image: %s" % img
            self.warnings.append(wrn)
            logger.warning(wrn)
            return

        img_path = os.path.join(self.images_folder, img)
        if not os.path.exists(img_path):
            wrn = "Unable to locate image: %s" % img
            self.warnings.append(wrn)
            logger.warning(wrn)
            return

        # check filename validity
        if not self._is_valid_image_filename(img):
            return

        out_path = os.path.join(self.images_output_folder, os.path.basename(img_path))
        logger.debug("#%d: copy img: %s" % (feature_idx, img_path))
        shutil.copy2(img_path, self.images_output_folder)

        if self.do_exif:

            img_ext = os.path.splitext(img)[-1].lower()
            if img_ext not in [".jpeg", ".jpg"]:
                logger.info("unsupported extension: %s" % img_ext)
                return

            try:
                self.geotag_jpeg(img_path=out_path, lat=feature.centroid.y, lon=feature.centroid.x)
                logger.debug("#%d: do exif: %s" % (feature_idx, out_path))
            except Exception as e:
                logger.debug("#%d: issue while doing exif: %s" % (feature_idx, e))

    @classmethod
    def geotag_jpeg(cls, img_path, lat, lon):
        exif_dict = piexif.load(img_path)
        # for key in exif_dict:
        #     logger.debug("%s: %s" % (key, exif_dict[key],))

        base = 10000
        lat = Geodesy.dd2dms(lat)
        # logger.debug("lat: %s" % (lat, ))
        lon = Geodesy.dd2dms(lon)
        # logger.debug("lon: %s" % (lon,))

        exif_dict["GPS"].clear()

        exif_dict["GPS"][piexif.GPSIFD.GPSVersionID] = (2, 3, 0, 0)

        if lat[0] > 0:
            exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = "N"
        else:
            exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = "S"
        exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] = ((abs(int(lat[0])), 1),
                                                       (int(lat[1]), 1),
                                                       (int(lat[2]*base), base))

        if lon[0] > 0:
            exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = "E"
        else:
            exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = "W"
        exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] = ((abs(int(lon[0])), 1),
                                                        (int(lon[1]), 1),
                                                        (int(lon[2]*base), base))

        exif_dict["GPS"][piexif.GPSIFD.GPSMapDatum] = "WGS-84"

        # remove
        for k in [piexif.GPSIFD.GPSAltitudeRef, piexif.GPSIFD.GPSAltitude, piexif.GPSIFD.GPSSatellites,
                  piexif.GPSIFD.GPSStatus, piexif.GPSIFD.GPSMeasureMode]:
            if k in exif_dict["GPS"].keys():
                del exif_dict["GPS"][k]

        exif_bytes = piexif.dump(exif_dict)

        im = Image.open(img_path)
        im.save(img_path, exif=exif_bytes)

    def _is_valid_image_filename(self, img_name):

        name = os.path.splitext(img_name)[0]

        if len(name) not in [28, 29]:
            wrn = "Invalid length for image name: %s" % name
            self.warnings.append(wrn)
            logger.warning(wrn)
            return False

        if not name[0].isalpha():
            wrn = "Invalid first character for image name: %s" % name
            self.warnings.append(wrn)
            logger.warning(wrn)
            return False

        for idx in [1, 2, 3, 4, 5]:
            if not name[idx].isnumeric():
                wrn = "Invalid character #%d for image name: %s" % (idx, name)
                self.warnings.append(wrn)
                logger.warning(wrn)
                return False

        for idx in [6, 13]:
            if not name[idx] == "_":
                wrn = "Invalid character #%d for image name: %s" % (idx, name)
                self.warnings.append(wrn)
                logger.warning(wrn)
                return False

        token = name[7:13]
        if not token == "SBDARE":
            wrn = "Invalid %s in image name: %s" % (token, name)
            self.warnings.append(wrn)
            logger.warning(wrn)
            return False

        return True

    def _calc_cmecs(self, info, feature_idx):

        if len(info.natsur_list) == 0:

            logger.error("feature #%d has not NATSUR")
            return info

        logger.debug("#%d: natsur (%d): %s, natqua (%d): %s" %
                     (feature_idx, len(info.natsur_list), info.natsur_list, len(info.natqua_list), info.natqua_list))

        # retrieve CMECS name and code
        subs = [0, 0]
        subs[0] = int(info.natsur_list[0])
        try:
            subs[1] = int(info.natqua_list[0])
        except (ValueError, IndexError):
            subs[1] = 0

        try:
            info.c_subn, info.c_subc = s57_to_cmecs(subs[0], subs[1])
            logger.debug("- subs %s -> %s, %s" % (subs, info.c_subn, info.c_subc))

        except KeyError:
            logger.error("- subs %s -> invalid pair for CMECS look-up" % (subs, ))
            return info

        # retrieve co-occurring element #1
        if (len(info.natqua_list) > 1) or (len(info.natsur_list) > 1):

            subs = [0, 0]

            try:
                subs[0] = int(info.natsur_list[1])
            except (ValueError, IndexError):
                subs[0] = 0

            try:
                subs[1] = int(info.natqua_list[1])
            except (ValueError, IndexError):
                subs[1] = 0

            try:
                info.c_cen1, info.c_cec1 = s57_to_cmecs(subs[0], subs[1])
                logger.debug("- coe1 %s -> %s, %s" % (subs, info.c_cen1, info.c_cec1))

            except KeyError:
                logger.error("- coe1 %s -> invalid pair for CMECS look-up" % (subs,))
                return info

        # retrieve co-occurring element #2
        if (len(info.natqua_list) > 2) or (len(info.natsur_list) > 2):

            subs = [0, 0]

            try:
                subs[0] = int(info.natsur_list[2])
            except (ValueError, IndexError):
                subs[0] = 0

            try:
                subs[1] = int(info.natqua_list[2])
            except (ValueError, IndexError):
                subs[1] = 0

            try:
                info.c_cen2, info.c_cec2 = s57_to_cmecs(subs[0], subs[1])
                logger.debug("- coe2 %s -> %s, %s" % (subs, info.c_cen2, info.c_cec2))

            except KeyError:
                logger.error("- coe2 %s -> invalid pair for CMECS look-up" % (subs, ))
                return info

        return info

    def _write_shape_attributes(self, ft, info):

        ft.SetField('obstim', info.observed_time)
        ft.SetField('COLOUR', info.colour)
        ft.SetField('NATQUA', info.natqua)
        ft.SetField('NATSUR', info.natsur)
        ft.SetField('remrks', info.remrks)
        ft.SetField('SORDAT', info.sordat)
        ft.SetField('SORIND', info.sorind)
        if info.image1 != "":
            ft.SetField('image1', os.path.join("Images", info.image1))
        if info.image2 != "":
            ft.SetField('image2', os.path.join("Images", info.image2))
        if info.image3 != "":
            ft.SetField('image3', os.path.join("Images", info.image3))
        if info.image4 != "":
            ft.SetField('image4', os.path.join("Images", info.image4))
        ft.SetField('c_subn', info.c_subn)
        ft.SetField('c_subc', info.c_subc)
        ft.SetField('c_cen1', info.c_cen1)
        ft.SetField('c_cec1', info.c_cec1)
        ft.SetField('c_cen2', info.c_cen2)
        ft.SetField('c_cec2', info.c_cec2)

    def _create_ogr_point_lyr_and_fields(self, ds):
        # create the only data layer
        lyr = ds.CreateLayer('qctools', None, ogr.wkbPoint)
        if lyr is None:
            logger.error("Layer creation failed")
            return

        field = ogr.FieldDefn('obstim', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('COLOUR', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('NATQUA', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('NATSUR', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('remrks', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('SORDAT', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('SORIND', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('image1', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('image2', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('image3', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('image4', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('c_subn', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('c_subc', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('c_cen1', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('c_cec1', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('c_cen2', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        field = ogr.FieldDefn('c_cec2', ogr.OFTString)
        field.SetWidth(254)
        if lyr.CreateField(field) != 0:
            raise RuntimeError("Creating field failed.")

        return lyr

    def _finalize_generate_output(self, root_folder, base_folder, remove_folder=True):

        try:

            if not self.has_images:
                blank_path = os.path.join(self.images_output_folder, "IntentionallyEmpty.txt")
                fid = open(blank_path, "w")
                fid.close()

            # shutil.copy(self.output_ascii, self.cmecs_output_folder)

            zipping_folder = os.path.join(root_folder, base_folder)

            shutil.make_archive(base_name=os.path.join(root_folder, "%s_shp_images" % base_folder),
                                format="zip",
                                root_dir=zipping_folder)

            if remove_folder:
                shutil.rmtree(zipping_folder)

            return True

        except Exception as e:

            logger.warning("While finalizing output: %s" % e)
            return False
