import logging

logger = logging.getLogger(__name__)


class Flags:

    def __init__(self):
        self.features = [[], [], [], []]

        # ### ALL FEATURES ###
        class AllFeatures:
            def __init__(self):
                self.redundancy = list()
                self.chars_limit = list()

            def nr_of_flagged(self) -> int:
                return len(self.redundancy) + len(self.chars_limit)

        self.all_fts = AllFeatures()

        # ### ASSIGNED FEATURES ###
        class AssignedFeatures:
            def __init__(self):
                self.description = list()
                self.remarks = list()

            def nr_of_flagged(self) -> int:
                return len(self.description) + len(self.remarks)

        self.ass_fts = AssignedFeatures()

        # ### NEW OR UPDATED FEATURES ###
        class NewUpdatedFeatures:
            def __init__(self):
                self.sorind = list()
                self.sorind_invalid = list()
                self.sordat = list()
                self.sordat_invalid = list()
                self.valsous_watlev = list()
                self.elevat = list()
                self.valsous_quasou = list()

            def nr_of_flagged(self) -> int:
                return len(self.sorind) + len(self.sorind_invalid) + \
                       len(self.sordat) + len(self.sordat_invalid) + \
                       len(self.valsous_watlev) + len(self.elevat) + \
                       len(self.valsous_quasou)

        self.new_updated_fts = NewUpdatedFeatures()

        # ### NEW OR DELETED FEATURES ###
        class NewDeletedFeatures:
            def __init__(self):
                self.remarks = list()
                self.recommend = list()

            def nr_of_flagged(self) -> int:
                return len(self.remarks) + len(self.recommend)

        self.new_deleted_fts = NewDeletedFeatures()

        # ### IMAGES ###
        class Images:
            def __init__(self):
                self.invalid_paths = list()
                self.invalid_names = list()


            def nr_of_flagged(self) -> int:
                return len(self.invalid_paths) + len(self.invalid_names)

        self.images = Images()

        # SOUNDINGS
        class Soundings:
            def __init__(self):
                self.tecsou = list()
                self.quasou = list()

            def nr_of_flagged(self) -> int:
                return len(self.tecsou) + len(self.quasou)

        self.soundings = Soundings()

        # DTONS
        class Dtons:
            def __init__(self):
                self.images = list()

            def nr_of_flagged(self) -> int:
                return len(self.images)

        self.dtons = Dtons()

        # WRECKS
        class Wrecks:
            def __init__(self):
                self.images = list()
                self.catwrk = list()
                self.watlev = list()
                self.unknown_watlev = list()
                self.valsou = list()
                self.tecsou = list()
                self.unknown_tecsou = list()
                self.quasou = list()
                self.unknown_quasou = list()

            def nr_of_flagged(self) -> int:
                return len(self.images) + len(self.catwrk) + \
                       len(self.watlev) + len(self.unknown_watlev) + \
                       len(self.valsou) + len(self.tecsou) + \
                       len(self.unknown_tecsou) + len(self.quasou) + \
                       len(self.unknown_quasou)

        self.wrecks = Wrecks()

        # ROCKS
        class Rocks:
            def __init__(self):
                self.valsou = list()
                self.watlev = list()
                self.unknown_watlev = list()
                self.quasou = list()
                self.unknown_quasou = list()
                self.tecsou = list()
                self.unknown_tecsou = list()

            def nr_of_flagged(self) -> int:
                return len(self.valsou) + len(self.watlev) + \
                       len(self.quasou) + len(self.tecsou) + \
                       len(self.unknown_watlev) + len(self.unknown_quasou) + \
                       len(self.unknown_tecsou)

        self.rocks = Rocks()

        # OBSTRUCTIONS
        class Obstructions:
            def __init__(self):
                self.images = list()
                self.valsou = list()
                self.watlev = list()
                self.unknown_watlev = list()
                self.quasou = list()
                self.unknown_quasou = list()
                self.tecsou = list()
                self.unknown_tecsou = list()
                self.foul_valsou = list()
                self.foul_ground_valsou = list()
                self.foul_ground_watlev = list()
                self.foul_ground_quasou = list()
                self.foul_ground_tecsou = list()
                self.foul_unknown_watlev = list()
                self.foul_unknown_tecsou = list()
                self.foul_unknown_quasou = list()

            def nr_of_flagged(self) -> int:
                return len(self.images) + len(self.valsou) + len(self.watlev) + len(self.unknown_watlev) + \
                       len(self.quasou) + + len(self.unknown_quasou) + len(self.tecsou) + len(self.unknown_tecsou) + \
                       len(self.foul_valsou) + len(self.foul_ground_valsou) + len(self.foul_ground_watlev) + \
                       len(self.foul_ground_quasou) + len(self.foul_ground_tecsou) + len(self.foul_unknown_watlev) + \
                       len(self.foul_unknown_tecsou) + len(self.foul_unknown_quasou)

        self.obstructions = Obstructions()

        # OFFSHORE PLATFORMS
        class Platforms:
            def __init__(self):
                self.images = list()

            def nr_of_flagged(self) -> int:
                return len(self.images)

        self.platforms = Platforms()

        # SEABED AREAS
        class Sbdares:
            def __init__(self):
                self.natsur = list()
                self.pt_natqua = list()
                self.pt_colour = list()
                self.pt_allowable_combo = list()
                self.watlev = list()

            def nr_of_flagged(self) -> int:
                return len(self.natsur) + len(self.pt_natqua) + \
                       len(self.pt_colour) + len(self.pt_allowable_combo) + \
                       len(self.watlev)

        self.sbdares = Sbdares()

        # MOORINGS
        class Moorings:
            def __init__(self):
                self.catmor = list()

            def nr_of_flagged(self) -> int:
                return len(self.catmor)

        self.moorings = Moorings()

        # COASTLINES
        class Coastlines:
            def __init__(self):
                self.coalne = list()
                self.slcons = list()

            def nr_of_flagged(self) -> int:
                return len(self.coalne) + len(self.slcons)

        self.coastlines = Coastlines()

        # LANDS
        class Lands:
            def __init__(self):
                self.elevat = list()

            def nr_of_flagged(self) -> int:
                return len(self.elevat)

        self.lands = Lands()

        # META COVERAGES
        class Coverages:
            def __init__(self):
                self.m_covr_catcov = list()
                self.m_covr_inform = list()
                self.m_covr_ninfom = list()

            def nr_of_flagged(self) -> int:
                return len(self.m_covr_catcov) + len(self.m_covr_inform) + \
                       len(self.m_covr_ninfom)

        self.coverages = Coverages()

        # OFFICE ONLY
        class Office:
            def __init__(self):
                self.without_onotes = list()
                self.hsdrec_empty = list()
                self.prohibited_kwds = list()
                self.fish_haven_kwds = list()
                self.mooring_buoy_kwds = list()
                self.atons = list()
                self.m_qual_catzoc = list()
                self.m_qual_sursta = list()
                self.m_qual_surend = list()
                self.m_qual_surend_sordat = list()
                self.m_qual_tecsou = list()
                self.mcd_description = list()
                self.mcd_remarks = list()
                self.chars_limit = list()

            def nr_of_flagged(self) -> int:
                return len(self.without_onotes) + len(self.hsdrec_empty) + \
                       len(self.prohibited_kwds) + len(self.fish_haven_kwds) + \
                       len(self.mooring_buoy_kwds) + + len(self.atons) + len(self.m_qual_catzoc) + \
                       len(self.m_qual_sursta) + len(self.m_qual_surend) + \
                       len(self.m_qual_tecsou) + len(self.mcd_description) + \
                       len(self.mcd_remarks) + len(self.chars_limit)

        self.office = Office()

    def append(self, x: float, y: float, note: str, info: str) -> None:
        """S57Aux function that append the note & info (if the feature position was already flagged) or add a new one"""

        # check if the point was already flagged for the same test
        for i in range(len(self.features[0])):
            if (self.features[0][i] == x) and (self.features[1][i] == y) and (info == self.features[3][i]):
                tokens = self.features[2][i].split('[x')
                if len(tokens) == 1:
                    self.features[2][i] = "%s [x2]" % note
                else:
                    self.features[2][i] = "%s [x%d]" % (note, int(tokens[1].split("]")[0]) + 1)
                return

        # if not flagged, just append the new flagged position
        self.features[0].append(x)
        self.features[1].append(y)
        self.features[2].append(note)
        self.features[3].append(info)
