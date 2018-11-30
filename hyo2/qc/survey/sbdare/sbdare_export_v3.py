import logging
logger = logging.getLogger(__name__)

from hyo2.qc.survey.sbdare.base_sbdare import BaseSbdare, sbdare_algos
from hyo2.qc.common.s57_aux import S57Aux
from hyo2.qc.common.geodesy import Geodesy


class SbdareExportV3(BaseSbdare):

    def __init__(self, s57):
        super().__init__(s57=s57)
        self.type = sbdare_algos["SBDARE_EXPORT_v3"]
        self.all_features = self.s57.rec10s
        self.sbdare_features = list()

        self.flagged_natsur = list()
        self.flagged_colour = list()

    def has_sbdare_issues(self):
        """Return true is there are issues with sbdare attributes"""

        natsur_flagged = len(self.flagged_natsur) > 0
        colour_flagged = len(self.flagged_colour) > 0
        return natsur_flagged or colour_flagged

    def run(self):
        """Execute the set of check of the SBDARE check algorithm"""

        self.sbdare_features = S57Aux.select_by_object(self.all_features, object_filter=['SBDARE', ])
        self.sbdare_features = S57Aux.select_only_points(self.sbdare_features)

    def generate_ascii(self, output_file):
        """All collected SBDARE objects are printed to an ASCII file per HTD 2013-3"""
        # create output file
        fod = open(output_file, 'w')

        # add header
        fod.write('Latitude;Longitude;Observed time;Colour;Nature of surface - qualifying terms;Nature of surface;'
                  'Remarks;Source date;Source indication\n')

        # for each SBDARE, write a row
        for feature in self.sbdare_features:

            # retrieve position
            lat = Geodesy.dd2dms(feature.centroid.y)
            lon = Geodesy.dd2dms(feature.centroid.x)
            lat_str = "%02.0f-%02.0f-%05.2f%s" % (abs(lat[0]), lat[1], lat[2], ("N" if (lat[0] > 0) else "S"))
            lon_str = "%03.0f-%02.0f-%05.2f%s" % (abs(lon[0]), lon[1], lon[2], ("E" if (lon[0] > 0) else "W"))
            # print(lat_str, lon_str)

            # retrieve attribute information
            observed_time = str()
            colour = str()
            natqua = str()
            natsur = str()
            remarks = str()
            sordat = str()
            sorind = str()
            for attribute in feature.attributes:
                if attribute.acronym == 'obstim':
                    observed_time = attribute.value
                elif attribute.acronym == 'COLOUR':
                    colour = attribute.value
                elif attribute.acronym == 'NATQUA':
                    natqua = attribute.value
                elif attribute.acronym == 'NATSUR':
                    natsur = attribute.value
                elif attribute.acronym == 'remrks':
                    remarks = attribute.value
                elif attribute.acronym == 'SORDAT':
                    sordat = attribute.value
                elif attribute.acronym == 'SORIND':
                    sorind = attribute.value

            # actually write the SBDARE row
            fod.write("%s;%s;%s;%s;%s;%s;%s;%s;%s\n"
                      % (lat_str, lon_str, observed_time, colour, natqua, natsur, remarks, sordat, sorind))

        fod.close()

        return True
