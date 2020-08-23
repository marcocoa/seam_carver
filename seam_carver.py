#!/usr/bin/env python

from PIL import Image
from scipy import ndimage
from progress.bar import Bar
import numpy as np
import argparse

SAVE_ENERGY_MAP = False

def main():
    args = parse_args()
    img = Image.open(args["in"])

    global SAVE_ENERGY_MAP
    SAVE_ENERGY_MAP = args["save_energy_map"]


    if args["remove_n_cols"] > 0:
        with Bar("Removing columns", max=args["remove_n_cols"]) as bar:
            for _ in range(args["remove_n_cols"]):
                bar.next()
                img = vertical_seam_carve(img)

    if args["remove_n_rows"] > 0:
        with Bar("Removing rows", max=args["remove_n_rows"]) as bar:
            img = img.rotate(90, expand=True)
            for _ in range(args["remove_n_rows"]):
                bar.next()
                img = vertical_seam_carve(img)
            img = img.rotate(-90, expand=True)

    if args["remove_n_cols"] > 0 or args["remove_n_rows"] > 0:
        img.save(args["out"])
        print("Image saved to {}".format(args["out"]))

def parse_args():
    parser = argparse.ArgumentParser(description="Seam carve an image")
    parser.add_argument("-in", required=True, help="Input image")
    parser.add_argument("-out", required=True, help="Output image")
    parser.add_argument("-rnc", "--remove-n-cols", type=int, default=0,
        help="Number of columns to remove")
    parser.add_argument("-rnr", "--remove-n-rows", type=int, default=0,
        help="Number of rows to remove")
    parser.add_argument("-sem", "--save-energy-map", action="store_true",
        help="Save the initial energy map to /tmp/energy.jpg")
    return vars(parser.parse_args())

def vertical_seam_carve(img):
    img_arr = np.asarray(img)
    rows, cols = len(img_arr), len(img_arr[0])

    seams = vertical_seams(img)
    seam = vertical_find_lowest_energy_seam(seams)

    # make a copy with one fewer column, since we'll be carving one out
    new_img = np.resize(img_arr, (rows, cols - 1, 3))
    for i in range(rows):
        for j in range(cols - 1):
            # remove the pixel on the seam by shifting all pixels to the right
            # of the seam one to the left
            if j < seam[i]:
                new_img[i][j] = img_arr[i][j]
            else:
                new_img[i][j] = img_arr[i][j+1]
    return Image.fromarray(new_img)

def vertical_find_lowest_energy_seam(energy):
    seam = [np.argmin(energy[-1])]
    for i in reversed(range(len(energy) - 1)):
        last_row_idx = seam[-1]
        idx, val = last_row_idx, energy[i][last_row_idx]
        if idx - 1 > 0:
            l_idx, l_val = idx - 1, energy[i][idx - 1]
            if l_val < val:
                idx, val = l_idx, l_val
        if idx + 1 < len(energy[i]):
            r_idx, r_val = idx + 1, energy[i][idx + 1]
            if r_val < val:
                idx, val = r_idx, r_val
        seam.append(idx)
    return seam

def vertical_seams(img):
    energy = gradient_magnitude(img)
    rows, cols = len(energy), len(energy[0])

    for i in range(1, rows):
        for j in range(0, cols):
            top_row_neighbors = [
                energy[i-1][j - 1 if j > 0 else j],
                energy[i-1][j],
                energy[i-1][j + 1 if j < cols - 1 else j]]
            energy[i][j] += min(top_row_neighbors)
    return energy

def gradient_magnitude(img):
    # Thank you, StackOverflow
    # https://stackoverflow.com/questions/49732726/how-to-compute-the-gradients-of-image-using-python

    # img_grey by default seems to be of type uint8, which has two issues:
    # 1. the resultant grad is of a rather low-precision type, which is prone to
    #    overflowing when calculating seams
    # 2. the grad ends up mega wonky and is *not* helpful towards finding good
    #    seams
    img_grey = np.asarray(img.convert('L')).astype("float64")
    sx = ndimage.sobel(img_grey, axis=0, mode="constant")
    sy = ndimage.sobel(img_grey, axis=1, mode="constant")
    grad = np.hypot(sx, sy)

    global SAVE_ENERGY_MAP
    if SAVE_ENERGY_MAP:
        SAVE_ENERGY_MAP = False
        Image.fromarray(grad).convert('L').save("/tmp/energy.jpg")

    return grad


if __name__ == "__main__":
    main()
