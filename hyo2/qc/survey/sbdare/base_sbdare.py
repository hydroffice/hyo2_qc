import logging

from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)

sbdare_algos = {
    "BASE": 0,
    "SBDARE_EXPORT_v3": 1,
    "SBDARE_EXPORT_v4": 2,
}


class BaseSbdare:
    def __init__(self, s57):
        self.type = sbdare_algos["BASE"]
        # inputs
        self.s57 = s57
        # outputs
        self.flagged_features = [[], [], []]

        self.warnings = list()

    def __repr__(self):
        msg = "  <BaseSbdare>\n"

        msg += "    <type: %s>\n" % Helper.first_match(sbdare_algos, self.type)
        msg += "    <s57: %s>\n" % bool(self.s57)
        msg += "    <flagged features: %s>\n" % len(self.flagged_features)

        return msg


def s57_to_cmecs(natsur, natqua):

    cmecs = dict()
    cmecs[0, 0] = ['', '']
    cmecs[1, 0] = ['Mud', 'S1.2.2.5']
    cmecs[2, 0] = ['Clay', 'S1.2.2.5.3']
    cmecs[3, 0] = ['Silt', 'S1.2.2.5.1']
    cmecs[4, 0] = ['Sand', 'S1.2.2.2']
    cmecs[5, 0] = ['Gravel', 'S1.2.1.1']
    cmecs[6, 0] = ['Granule', 'S1.2.1.1.4']
    cmecs[7, 0] = ['Pebble', 'S1.2.1.1.3']
    cmecs[8, 0] = ['Cobble', 'S1.2.1.1.2']
    cmecs[9, 0] = ['Rock', 'S1.1']
    cmecs[11, 0] = ['Rock', 'S1.1']
    cmecs[14, 0] = ['Coral', 'S2.2']
    cmecs[17, 0] = ['Shell', 'S2.5']
    cmecs[18, 0] = ['Boulder', 'S1.2.1.1.1']
    cmecs[4, 1] = ['Fine Sand', 'S1.2.2.2.4']
    cmecs[4, 2] = ['Medium Sand', 'S1.2.2.2.3']
    cmecs[4, 3] = ['Coarse Sand', 'S1.2.2.2.2']
    cmecs[4, 6] = ['Soft Sand', 'S1.2.2.2(I03)']
    cmecs[4, 8] = ['Volcaniclastic Sand', 'S1.2.2.2(SD13)']
    cmecs[4, 9] = ['Carbonate Sand', 'S1.2.2.2(SD01)']
    cmecs[4, 10] = ['Hard Sand', 'S1.2.2.2(I01)']
    cmecs[14, 4] = ['Coral Hash', 'S2.2.3']
    cmecs[17, 4] = ['Shell Hash', 'S2.5.3']
    cmecs[17, 9] = ['Carbonate Shells', 'S2.5(SD01']
    cmecs[18, 8] = ['Volcaniclastic Boulder', 'S1.2.1.1.1(SD13)']
    cmecs[18, 9] = ['Carbonate Boulder', 'S1.2.1.1.1(SD01)']
    cmecs[11, 8] = ['Volcaniclastic Rock', 'S1.1(SD13)']
    cmecs[9, 8] = ['Volcaniclastic Rock', 'S1.1(SD13)']
    cmecs[9, 9] = ['Carbonate Rock', 'S1.1(SD01)']
    cmecs[8, 8] = ['Volcaniclastic Cobble', 'S1.2.1.1.2(SD13)']
    cmecs[8, 9] = ['Carbonate Cobble', 'S1.2.1.1.2(SD01)']
    cmecs[7, 8] = ['Volcaniclastic Pebble', 'S1.2.1.1.3(SD13)']
    cmecs[7, 9] = ['Carbonate Pebble', 'S1.2.1.1.3(SD01)']
    cmecs[6, 8] = ['Volcaniclastic Granule', 'S1.2.1.1.4(SD13)']
    cmecs[6, 9] = ['Carbonate Granule', 'S1.2.1.1.4(SD01)']
    cmecs[5, 8] = ['Volcaniclastic Gravel', 'S1.2.1.1(SD13)']
    cmecs[5, 9] = ['Carbonate Gravel', 'S1.2.1.1(SD01)']
    cmecs[3, 5] = ['Silt', 'S1.2.2.5.1']
    cmecs[3, 6] = ['Soft Silt', 'S1.2.2.5.1(I03)']
    cmecs[3, 7] = ['Silt', 'S1.2.2.5.1']
    cmecs[3, 10] = ['Hard Silt', 'S1.2.2.5.1(I01)']
    cmecs[2, 5] = ['Clay', 'S1.2.2.5.3']
    cmecs[2, 6] = ['Soft Clay', 'S1.2.2.5.3(I03)']
    cmecs[2, 7] = ['Clay', 'S1.2.2.5.3']
    cmecs[2, 10] = ['Hard Clay', 'S1.2.2.5.3(I01)']
    cmecs[1, 5] = ['Mud', 'S1.2.2.5']
    cmecs[1, 6] = ['Soft Mud', 'S1.2.2.5(I03)']
    cmecs[1, 7] = ['Mud', 'S1.2.2.5']
    cmecs[1, 8] = ['Volcaniclastic Mud', 'S1.2.2.5(SD13)']
    cmecs[1, 9] = ['Carbonate Mud', 'S1.2.2.5(SD01)']
    cmecs[1, 10] = ['Hard Mud', 'S1.2.2.5(I01)']

    return cmecs[natsur, natqua]
