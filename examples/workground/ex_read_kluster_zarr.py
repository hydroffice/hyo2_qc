import matplotlib.pyplot as plt
from bathygrid.convenience import load_grid


zarr_path = r"C:\Users\gmasetti\Documents\kluster\test\srgrid_mean_auto_20210926_145921"

bg = load_grid(folder_path=zarr_path)

# Grid
print("bbox: %f, %f, %f, %f" % (bg.min_x, bg.max_x, bg.min_y, bg.max_y))
print("shape: %s, %s" % (bg.width, bg.height))

# BaseGrid
print("origin: %f, %f" % (bg.origin_x, bg.origin_y))
print("data: %s" % (bg.data))
print("container: %s" % (bg.container))
print("tiles: %s" % (bg.tiles))
print("tile origin: %s, %s" % (bg.tile_x_origin, bg.tile_y_origin))
print("tile edges: %s, %s" % (bg.tile_edges_x, bg.tile_edges_y))
print("nr of tiles/maximum: %s/%s" % (bg.number_of_tiles, bg.maximum_tiles))
print("tile size: %s" % bg.tile_size)
print("points count: %s" % bg.points_count)

# BathyGrid
print("mean depth: %.3f" % bg.mean_depth)
print("epgs: %s" % bg.epsg)
print("vertical reference: %s" % bg.vertical_reference)
print("resolutions: %s" % bg.resolutions)
print("name: %s" % bg.name)
print("grid algorithm: %s" % bg.grid_algorithm)
print("grid resolution: %s" % bg.grid_resolution)
print("layer names: %s" % bg.layer_names)

for tile in bg.tiles.flat:
    if tile is None:
        continue
    print("\n- %s" % tile.cells)
    print("cell count: %s" % tile.cell_count)

dl = bg.get_layers_by_name()
print(dl)
print(type(dl))

plt.figure()
bg.plot()
plt.show()