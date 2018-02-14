# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from PIL import Image
import numpy
import os

def _filenames(topdir, prefix, suffix):
    for dirpath, dirnames, filenames in os.walk(topdir):
        for filename in filenames:
            if not filename.startswith(prefix):
                continue
            if not filename.endswith(suffix):
                continue
            index = filename[len(prefix):-len(suffix)]
            try:
                index = int(index)
            except ValueError:
                continue
            yield index, os.path.join(dirpath, filename)

def filenames(*args):
    unique = {}
    for index, filename in _filenames(*args):
        assert not index in unique
        unique[index] = filename
    for index, filename in sorted(unique.items()):
        yield filename

class Overlayer(object):
    def __init__(self):
        self.totals = None

    def push(self, filename):
        print(filename)
        index = int(filename[-8:-4])
        img = Image.open(filename)
        if self.totals is None:
            self.camera = filename.split(os.sep, 5)[-2]
            self.__size = img.size
            print("Initializing", self.__size)
            self.totals = numpy.zeros((self.__size[1], self.__size[0], 3),
                                      dtype=numpy.int64)
        if cmp(*img.size) != cmp(*self.__size):
            img = img.transpose(Image.ROTATE_270)
        if img.size != self.__size:
            scale = [i / s for i, s in zip(img.size, self.__size)]
            if (1 - scale[0] / scale[1]) > 0.005:
                print("\x1B[31m%s %s\x1B[0m" % (img.size, scale))
                #raise AssertionError
            img = img.resize(self.__size, Image.ANTIALIAS)
        self.totals += numpy.array(img)
        self.__last = index

    def output(self):
        img = self.totals.copy()
        tmp = img.min()
        print("min =", tmp,)
        img -= tmp
        tmp = img.max()
        print("max =", tmp)
        img *= 255
        img //= tmp
        img = Image.frombytes("RGB", self.__size,
                              img.astype(numpy.int8).tostring())
        img.save("%s-%04d.png" % (self.camera, self.__last))

if __name__ == "__main__":
    ol = Overlayer()
    for filename in filenames(os.path.join(os.environ["HOME"],
                                           "Pictures", "dsc"),
                              "dsc_", ".jpg"):
        try:
            ol.push(filename)
        except:
            break
    else:
        print("All done!")
    ol.output()
