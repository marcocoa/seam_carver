# seam_carver.py
A small seam carving script written in Python supporting the removal of vertical and horizontal seams from an image.


## Seam Carving Background
[Seam carving](https://en.wikipedia.org/wiki/Seam_carving) is a neat technique popularized by Photoshop as "content aware" fill/remove/patch/scale. In short, the technique works by calculating the energy of each pixel in the image and then finding and removing the contiguous line or "seam" with the least cumulative energy. There are various different methods with their own pros and cons for calculating each pixel's energy; this tool uses gradient magnitude.


## Requirements
* python3
* argparse
* PIL
* scipy
* progress
* numpy


I believe both argparse and PIL are included by default with most python3 installations. The rest can be installed via `pip`.


## Usage
./seam_carver.py [-h] -in IN -out OUT [-rnc REMOVE_N_COLS] [-rnr REMOVE_N_ROWS] [-sem]


## Future goals
* Performance improvements? Currently a 1280x720 image takes about 0.20-0.25s/seam on my 10th gen Core i7 ultraportable. This seems reasonably fast, but I want to know if it can go faster.
    - Implement a `--sloppy` mode that does not recalculate the gradient/energy for each iteration, potentially?
* Implement adding new seams to make an image larger.
* Implement masking in order to protect/remove a specific region.
* Implement different energy-computing backends/algorithms.


## Samples

Results, at least with the current gradient magnitude backend, are ... mixed. Some carves, while not perfect do look pretty good. For example here are vertical carves of the classic tower image and of a San Francisco skyline:

<img src="https://i.imgur.com/i8RGVVK.jpg" style="zoom:33%;" /> <img src="https://i.imgur.com/iHO4e3V.jpg" style="zoom:33%;" />

<img src="https://i.imgur.com/qaYOOnp.jpg" style="zoom: 25%;" /> <img src="https://i.imgur.com/7OI8QtB.jpg" style="zoom: 25%;" />



But then others like this horizontal carve of a koala look rather awful. Though, to be fair, the image probably lends itself better to a regular crop anyway:

<img src="https://i.imgur.com/Wlrbbxi.jpg" style="zoom:67%;" /> <img src="https://i.imgur.com/hJY1v2W.jpg" style="zoom:67%;" />


## Resources and Acknowledgements
For the idea to use numba:
* https://karthikkaranth.me/blog/implementing-seam-carving-with-python/
* https://github.com/andrewdcampbell/seam-carving

StackOverflow and Wikipedia, of course, for general knowledge on numpy, PIL, scipy, seam carving, and more specifically an easy way to calculate gradient magnitude:
* https://stackoverflow.com/questions/49732726/how-to-compute-the-gradients-of-image-using-python
* https://en.wikipedia.org/wiki/Seam_carving
