import logging

logger = logging.getLogger(__name__)


class Flags:
    
    def __init__(self):
        self.features = [[], [], []]

        # ### ALL FEATURES ###
        self.redundancy = list()

        # ### NEW OR UPDATED FEATURES ###
        self.sorind = list()
        self.sorind_invalid = list()
        self.sordat = list()
        self.sordat_invalid = list()
        self.new_valsous_watlev = list()
        self.new_elevat = list()
        self.new_valsous_quasou = list()

        # ### ASSIGNED FEATURES ###
        self.description = list()
        self.remarks = list()

        # ### NEW OR DELETED FEATURES ###
        self.remarks_features = list()
        self.recommend_features = list()

        # ### IMAGES ###
        self.images_features = list()
        self.images_hssd = list()
        self.images_non_sbdare = list()
        self.images_sbdare_points = list()
        self.images_sbdare_lines_areas = list()

        # SOUNDINGS
        self.soundings_tecsou = list()
        self.soundings_quasou = list()

        # DTONS
        self.dtons = list()

        # WRECKS
        self.wrecks_images = list()
        self.awois_features_1 = list()
        self.awois_features_2 = list()
        self.wrecks_catwrk = list()
        self.wrecks_watlev = list()
        self.wrecks_unknown_watlev = list()
        self.wrecks_valsou = list()
        self.wrecks_tecsou = list()
        self.wrecks_unknown_tecsou = list()
        self.wrecks_quasou = list()
        self.wrecks_unknown_quasou = list()

        # ROCKS
        self.uwtroc_valsou = list()
        self.uwtroc_watlev = list()
        self.uwtroc_unknown_watlev = list()
        self.uwtroc_quasou = list()
        self.uwtroc_unknown_quasou = list()
        self.uwtroc_tecsou = list()
        self.uwtroc_unknown_tecsou = list()

        # OBSTRUCTIONS
        self.obstrn_images = list()
        self.obstrn_points_valsou = list()
        self.obstrn_points_watlev = list()
        self.obstrn_lines_areas_watlev = list()
        self.obstrn_watlev_known = list()
        self.obstrn_watlev_undefined = list()
        self.obstrn_quasou = list()
        self.obstrn_unknown_quasou = list()
        self.obstrn_tecsou = list()
        self.obstrn_unknown_tecsou = list()
        self.obstrn_foul_valsou = list()
        self.obstrn_unknown_valsou = list()

        # OFFSHORE PLATFORMS
        self.ofsplf = list()

        # SEABED AREAS
        self.sbdare_natsur = list()
        self.sbdare_pt_natqua = list()
        self.sbdare_pt_colour = list()
        self.sbdare_pt_allowable_combo = list()
        self.sbdare_2 = list()
        self.sbdare_watlev = list()

        # MOORINGS
        self.morfac = list()

        # COASTLINES
        self.coalne = list()
        self.slcons = list()

        # LANDS
        self.lndelv = list()

        # META COVERAGES

        self.m_covr_catcov = list()
        self.m_covr_inform = list()
        self.m_covr_ninfom = list()

        # OFFICE ONLY

        self.without_onotes = list()
        self.hsdrec_empty = list()
        self.prohibited_kwds = list()
        self.fish_haven_kwds = list()
        self.mooring_buoy_kwds = list()
        self.m_qual_catzoc = list()
        self.m_qual_sursta = list()
        self.m_qual_surend = list()
        self.m_qual_surend_sordat = list()
        self.m_qual_tecsou = list()
        self.mcd_description = list()
        self.mcd_remarks = list()
        self.character_limit = list()

    def append(self, x: float, y: float, note: str) -> None:
        """S57Aux function that append the note (if the feature position was already flagged) or add a new one"""
        # check if the point was already flagged
        for i in range(len(self.features[0])):
            if (self.features[0][i] == x) and (self.features[1][i] == y):
                self.features[2][i] = "%s, %s" % (self.features[2][i], note)
                return

        # if not flagged, just append the new flagged position
        self.features[0].append(x)
        self.features[1].append(y)
        self.features[2].append(note)