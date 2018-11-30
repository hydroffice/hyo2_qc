from osgeo import gdal
import os
# this allows GDAL to throw Python Exceptions
gdal.UseExceptions()


class Data:

    def __init__(self):
        self.depth_path = "G:\\chrt\\H11077_WoodsHole\\Output\grids\\H110077_WoodsHole_depth.asc"
        self.depth = None
        self.depth_no_data = None
        self.depth_rows = None
        self.depth_cols = None
        self.depth_x_min = None
        self.depth_y_max = None
        self.depth_y_min = None
        self.depth_res = None

        self.std_dev_path = "G:\\chrt\\H11077_WoodsHole\\Output\grids\\H110077_WoodsHole_std_dev.asc"
        self.std_dev = None
        self.std_dev_no_data = None
        self.std_dev_rows = None
        self.std_dev_cols = None
        self.std_dev_x_min = None
        self.std_dev_y_max = None
        self.std_dev_y_min = None
        self.std_dev_res = None

        self.points_folder = "G:\\chrt\\H11077_WoodsHole\\Output\\pointcloud"

    def read_input_grids(self):

        # depth

        try:
            ds = gdal.Open(self.depth_path)

        except RuntimeError as e:
            print('While opening %s, %s' % (self.depth_path, e))
            return False

        try:
            self.depth = ds.GetRasterBand(1).ReadAsArray()

        except RuntimeError as e:
            print('While reading band, %s' % (e, ))
            return False

        self.depth_no_data = ds.GetRasterBand(1).GetNoDataValue()

        ulx, xres, xskew, uly, yskew, yres = ds.GetGeoTransform()
        self.depth_res = xres
        self.depth_rows = self.depth.shape[0]
        self.depth_cols = self.depth.shape[1]
        self.depth_x_min = ulx + self.depth_res / 2.0
        self.depth_y_max = uly + self.depth_res / 2.0
        self.depth_y_min = uly + yres * self.depth_rows + self.depth_res / 2.0
        # print(ulx, xres, xskew, uly, yskew, yres)

        # std dev

        try:
            ds = gdal.Open(self.std_dev_path)

        except RuntimeError as e:
            print('While opening %s, %s' % (self.std_dev_path, e))
            return False

        try:
            self.std_dev = ds.GetRasterBand(1).ReadAsArray()

        except RuntimeError as e:
            print('While reading band, %s' % (e, ))
            return False

        self.std_dev_no_data = ds.GetRasterBand(1).GetNoDataValue()

        ulx, xres, xskew, uly, yskew, yres = ds.GetGeoTransform()
        self.std_dev_res = xres
        self.std_dev_rows = self.std_dev.shape[0]
        self.std_dev_cols = self.std_dev.shape[1]
        self.std_dev_x_min = ulx + self.std_dev_res / 2.0
        self.std_dev_y_max = uly + self.std_dev_res / 2.0
        self.std_dev_y_min = uly + yres * self.std_dev_rows + self.std_dev_res / 2.0

        return True

    def calc_zscores(self):
        if not os.path.exists(self.points_folder):
            raise RuntimeError("the folder with sounding files does not exist")
        points_files = os.listdir(self.points_folder)

        for count, file in enumerate(points_files):

            # if count > 1:
            #     break

            # print("#%s -> %s" % (count, file))
            if os.path.splitext(file)[-1] != ".txt":
               continue
            self.read_and_write_points_per_file(in_file=file)

        return True

    def read_and_write_points_per_file(self, in_file):

        in_path = os.path.join(self.points_folder, in_file)
        out_path = os.path.join(self.points_folder + "_with_zs", in_file)
        print("input: %s" % in_path)
        print("output: %s" % out_path)

        with open(in_path) as fid:
            with open(out_path, "w") as fod:

                fid_rows = fid.readlines()
                fod_out = str()
                for fid_row in fid_rows:
                    in_tokens = fid_row.split()

                    col = round((float(in_tokens[0]) - self.depth_x_min) / self.depth_res)
                    row = round((self.depth_y_max - float(in_tokens[1])) / self.depth_res)
                    sounding_z = float(in_tokens[2])
                    sounding_vr_std_dev = float(in_tokens[6]) / 1.96
                    if (col < 0) or (row < 0) or (col >= self.depth_cols) or (row >= self.depth_rows):
                        node_z = self.depth_no_data
                        node_std_dev = self.depth_no_data
                        zs1 = self.depth_no_data
                        zs2 = self.depth_no_data
                    else:
                        node_z = self.depth[row, col]
                        node_std_dev = self.std_dev[row, col]

                        if (node_z == self.depth_no_data) or (node_std_dev == self.std_dev_no_data) \
                                or (node_std_dev == 0.0) or (sounding_vr_std_dev == 0.0):
                            zs1 = self.depth_no_data
                            zs2 = self.depth_no_data
                        else:
                            zs1 = (node_z - sounding_z) / sounding_vr_std_dev
                            zs2 = (node_z - sounding_z) / node_std_dev

                    print("sounding: (%s, %s, %s) -> vr std dev: %s" % (row, col, sounding_z, sounding_vr_std_dev))
                    print("node: (%s, %s, %s) -> std dev: %s" % (row, col, node_z, node_std_dev))
                    print("zs1: %.2f, zs2: %.2f" % (zs1, zs2))

                    fod_out += "%s %s %s %s %s %s %s %.3f %.3f\n" \
                               % (in_tokens[0], in_tokens[1], in_tokens[2],
                                  in_tokens[3], in_tokens[4], in_tokens[5], in_tokens[6],
                                  zs1, zs2)

                fod.write(fod_out)

    def flip_values(cls, in_file, nodata=-99999.0, skip=5):

        print("input: %s" % in_file)
        out_str = str()

        with open(in_file) as fid:

            in_rows = fid.readlines()
            for i, in_row in enumerate(in_rows):

                if i % 100 == 0:
                    print(i)

                if i <= skip:
                    out_str += in_row

                else:

                    in_tokens = in_row.split()
                    for in_token in in_tokens:
                        value = float(in_token)
                        if value != nodata:
                            value = -value
                        out_str += " %.3f" % value
                    out_str += "\n"

        print(out_str)
        with open(in_file, "w") as fod:
            fod.write(out_str)


    def __repr__(self):
        msg = "Data\n"

        msg += "  Depth:\n"
        msg += "  - shape: %s, %s\n" % (self.depth_rows, self.depth_cols)
        msg += "  - x min: %s\n" % self.depth_x_min
        msg += "  - y min: %s\n" % self.depth_y_min
        msg += "  - res: %s\n" % self.depth_res

        msg += "  Std Dev:\n"
        msg += "  - shape: %s, %s\n" % (self.std_dev_rows, self.std_dev_cols)

        return msg


data = Data()

# data.flip_values(data.depth_path)

success = data.read_input_grids()
if not success:
    exit(1)

success = data.calc_zscores()
if not success:
    exit(1)

print("%s" % data)
