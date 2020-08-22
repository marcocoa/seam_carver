#!/usr/bin/env python

from PIL import Image
from scipy import ndimage
from progress.bar import Bar
import numpy as np
import argparse


def main():
    args = parse_args()
    img = Image.open(args["in"])

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
    return vars(parser.parse_args())

def vertical_seam_carve(img):
    img_arr = np.asarray(img)
    rows, cols = len(img_arr), len(img_arr[0])

    energy = vertical_energy_map(img)
    seam = vertical_find_seam(energy)

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

def vertical_find_seam(energy):
    seam = [np.argmin(energy[-1])]
    for i in reversed(range(len(energy) - 1)):
        last = seam[-1]

        # pretty gross solution to find the index of the pixel to remove
        potential_next = (last, energy[i][last])
        if potential_next[0] - 1 > 0:
            potential_next2 = (potential_next[0] - 1, energy[i][potential_next[0] - 1])
            if potential_next2[1] < potential_next[1]:
                potential_next = potential_next2

        if potential_next[0] + 1 < len(energy[i]):
            potential_next2 = (potential_next[0] + 1, energy[i][potential_next[0] + 1])
            if potential_next2[1] < potential_next[1]:
                potential_next = potential_next2
        next_pixel = potential_next
        seam.append(next_pixel[0])
    return seam

def vertical_energy_map(img):
    grad = compute_grad(img)
    rows, cols = len(grad), len(grad[0])

    energy = grad.copy()
    for i in range(1, rows):
        for j in range(0, cols):
            top_row_neighbors = [
                energy[i-1][j - 1 if j > 0 else j],
                energy[i-1][j],
                energy[i-1][j + 1 if j < cols - 1 else j]]
            energy[i][j] += min(top_row_neighbors)
    return energy

def compute_grad(img):
    # Thank you, StackOverflow
    # https://stackoverflow.com/questions/49732726/how-to-compute-the-gradients-of-image-using-python
    img_grey = np.asarray(img.convert('L'))
    sx = ndimage.sobel(img_grey, axis=0, mode="constant")
    sy = ndimage.sobel(img_grey, axis=1, mode="constant")
    return np.hypot(sx, sy)


if __name__ == "__main__":
    main()
