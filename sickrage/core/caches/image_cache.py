# Author: echel0n <echel0n@sickrage.ca>
# URL: https://sickrage.ca
# Git: https://git.sickrage.ca/SiCKRAGE/sickrage.git
#
# This file is part of SiCKRAGE.
#
# SiCKRAGE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SiCKRAGE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SiCKRAGE.  If not, see <http://www.gnu.org/licenses/>.


import os

from hachoir.core import config as hachoir_config
from hachoir.metadata import extractMetadata
from hachoir.parser import guessParser
from hachoir.stream import StringInputStream

import sickrage
from sickrage.core.helpers import copy_file
from sickrage.metadata import GenericMetadata


class ImageCache(object):
    def __init__(self):
        hachoir_config.quiet = True

    def __del__(self):
        pass

    def _cache_dir(self):
        """
        Builds up the full path to the image cache directory
        """
        return os.path.abspath(os.path.join(sickrage.app.cache_dir, 'images'))

    def _thumbnails_dir(self):
        """
        Builds up the full path to the thumbnails image cache directory
        """
        return os.path.abspath(os.path.join(self._cache_dir(), 'thumbnails'))

    def poster_path(self, indexer_id):
        """
        Builds up the path to a poster cache for a given Indexer ID

        :param indexer_id: ID of the show to use in the file name
        :return: a full path to the cached poster file for the given Indexer ID
        """
        poster_file_name = str(indexer_id) + '.poster.jpg'
        return os.path.join(self._cache_dir(), poster_file_name)

    def banner_path(self, indexer_id):
        """
        Builds up the path to a banner cache for a given Indexer ID

        :param indexer_id: ID of the show to use in the file name
        :return: a full path to the cached banner file for the given Indexer ID
        """
        banner_file_name = str(indexer_id) + '.banner.jpg'
        return os.path.join(self._cache_dir(), banner_file_name)

    def fanart_path(self, indexer_id):
        """
        Builds up the path to a fanart cache for a given Indexer ID

        :param indexer_id: ID of the show to use in the file name
        :return: a full path to the cached fanart file for the given Indexer ID
        """
        fanart_file_name = str(indexer_id) + '.fanart.jpg'
        return os.path.join(self._cache_dir(), fanart_file_name)

    def fanart_thumb_path(self, indexer_id):
        """
        Builds up the path to a poster thumb cache for a given Indexer ID

        :param indexer_id: ID of the show to use in the file name
        :return: a full path to the cached poster thumb file for the given Indexer ID
        """
        fanartthumb_file_name = str(indexer_id) + '.fanart.jpg'
        return os.path.join(self._thumbnails_dir(), fanartthumb_file_name)

    def poster_thumb_path(self, indexer_id):
        """
        Builds up the path to a poster thumb cache for a given Indexer ID

        :param indexer_id: ID of the show to use in the file name
        :return: a full path to the cached poster thumb file for the given Indexer ID
        """
        posterthumb_file_name = str(indexer_id) + '.poster.jpg'
        return os.path.join(self._thumbnails_dir(), posterthumb_file_name)

    def banner_thumb_path(self, indexer_id):
        """
        Builds up the path to a banner thumb cache for a given Indexer ID

        :param indexer_id: ID of the show to use in the file name
        :return: a full path to the cached banner thumb file for the given Indexer ID
        """
        bannerthumb_file_name = str(indexer_id) + '.banner.jpg'
        return os.path.join(self._thumbnails_dir(), bannerthumb_file_name)

    def has_poster(self, indexer_id):
        """
        Returns true if a cached poster exists for the given Indexer ID
        """
        poster_path = self.poster_path(indexer_id)
        sickrage.app.log.debug("Checking if file " + str(poster_path) + " exists")
        return os.path.isfile(poster_path)

    def has_banner(self, indexer_id):
        """
        Returns true if a cached banner exists for the given Indexer ID
        """
        banner_path = self.banner_path(indexer_id)
        sickrage.app.log.debug("Checking if file " + str(banner_path) + " exists")
        return os.path.isfile(banner_path)

    def has_fanart(self, indexer_id):
        """
        Returns true if a cached fanart exists for the given Indexer ID
        """
        fanart_path = self.fanart_path(indexer_id)
        sickrage.app.log.debug("Checking if file " + str(fanart_path) + " exists")
        return os.path.isfile(fanart_path)

    def has_poster_thumbnail(self, indexer_id):
        """
        Returns true if a cached poster thumbnail exists for the given Indexer ID
        """
        poster_thumb_path = self.poster_thumb_path(indexer_id)
        sickrage.app.log.debug("Checking if file " + str(poster_thumb_path) + " exists")
        return os.path.isfile(poster_thumb_path)

    def has_banner_thumbnail(self, indexer_id):
        """
        Returns true if a cached banner exists for the given Indexer ID
        """
        banner_thumb_path = self.banner_thumb_path(indexer_id)
        sickrage.app.log.debug("Checking if file " + str(banner_thumb_path) + " exists")
        return os.path.isfile(banner_thumb_path)

    BANNER = 1
    POSTER = 2
    BANNER_THUMB = 3
    POSTER_THUMB = 4
    FANART = 5
    FANART_THUMB = 6

    def which_type(self, path):
        """
        Analyzes the image provided and attempts to determine whether it is a poster or banner.

        :param path: full path to the image
        :return: BANNER, POSTER if it concluded one or the other, or None if the image was neither (or didn't exist)
        """

        if not os.path.isfile(path):
            sickrage.app.log.warning("Couldn't check the type of " + str(path) + " cause it doesn't exist")
            return None

        with open(path, 'rb') as fh:
            img_metadata = extractMetadata(guessParser(StringInputStream(fh.read())))
            if not img_metadata:
                sickrage.app.log.debug(
                    "Unable to get metadata from " + str(path) + ", not using your existing image")
                return None

            img_ratio = float(img_metadata.get('width', 0)) / float(img_metadata.get('height', 0))

            # most posters are around 0.68 width/height ratio (eg. 680/1000)
            if 0.55 < img_ratio < 0.8:
                return self.POSTER

            # most banners are around 5.4 width/height ratio (eg. 758/140)
            elif 5 < img_ratio < 6:
                return self.BANNER

            # most fanart are around 1.77777 width/height ratio (eg. 1280/720 and 1920/1080)
            elif 1.7 < img_ratio < 1.8:
                return self.FANART
            else:
                sickrage.app.log.warning("Image has size ratio of " + str(img_ratio) + ", unknown type")

    def _cache_image_from_file(self, image_path, img_type, indexer_id):
        """
        Takes the image provided and copies it to the cache folder

        :param image_path: path to the image we're caching
        :param img_type: BANNER or POSTER or FANART
        :param indexer_id: id of the show this image belongs to
        :return: bool representing success
        """

        # generate the path based on the type & indexer_id
        if img_type == self.POSTER:
            dest_path = self.poster_path(indexer_id)
        elif img_type == self.BANNER:
            dest_path = self.banner_path(indexer_id)
        elif img_type == self.FANART:
            dest_path = self.fanart_path(indexer_id)
        else:
            sickrage.app.log.error("Invalid cache image type: " + str(img_type))
            return False

        # make sure the cache folder exists before we try copying to it
        if not os.path.isdir(self._cache_dir()):
            sickrage.app.log.info("Image cache dir didn't exist, creating it at " + str(self._cache_dir()))
            os.makedirs(self._cache_dir())

        if not os.path.isdir(self._thumbnails_dir()):
            sickrage.app.log.info(
                "Thumbnails cache dir didn't exist, creating it at " + str(self._thumbnails_dir()))
            os.makedirs(self._thumbnails_dir())

        sickrage.app.log.info("Copying from " + image_path + " to " + dest_path)
        copy_file(image_path, dest_path)

        return True

    def _cache_image_from_indexer(self, show_obj, img_type, force=False):
        """
        Retrieves an image of the type specified from indexer and saves it to the cache folder

        :param show_obj: TVShow object that we want to cache an image for
        :param img_type: BANNER or POSTER or FANART
        :return: bool representing success
        """

        # generate the path based on the type & indexer_id
        if img_type == self.POSTER:
            img_type_name = 'poster'
            dest_path = self.poster_path(show_obj.indexer_id)
        elif img_type == self.BANNER:
            img_type_name = 'series'
            dest_path = self.banner_path(show_obj.indexer_id)
        elif img_type == self.FANART:
            img_type_name = 'fanart'
            dest_path = self.fanart_path(show_obj.indexer_id)
        elif img_type == self.POSTER_THUMB:
            img_type_name = 'poster_thumb'
            dest_path = self.poster_thumb_path(show_obj.indexer_id)
        elif img_type == self.BANNER_THUMB:
            img_type_name = 'series_thumb'
            dest_path = self.banner_thumb_path(show_obj.indexer_id)
        elif img_type == self.FANART_THUMB:
            img_type_name = 'fanart_thumb'
            dest_path = self.fanart_thumb_path(show_obj.indexer_id)
        else:
            sickrage.app.log.error("Invalid cache image type: " + str(img_type))
            return False

        # retrieve the image from indexer using the generic metadata class
        metadata_generator = GenericMetadata()
        img_data = metadata_generator._retrieve_show_image(img_type_name, show_obj)
        result = metadata_generator._write_image(img_data, dest_path, force)

        return result

    def fill_cache(self, show_obj, force=False):
        """
        Caches all images for the given show. Copies them from the show dir if possible, or
        downloads them from indexer if they aren't in the show dir.

        :param show_obj: TVShow object to cache images for
        """

        sickrage.app.log.debug("Checking if we need any cache images for show " + str(show_obj.indexer_id))

        # check if the images are already cached or not
        need_images = {self.POSTER: force or not self.has_poster(show_obj.indexer_id),
                       self.BANNER: force or not self.has_banner(show_obj.indexer_id),
                       self.POSTER_THUMB: force or not self.has_poster_thumbnail(show_obj.indexer_id),
                       self.BANNER_THUMB: force or not self.has_banner_thumbnail(show_obj.indexer_id),
                       self.FANART: force or not self.has_fanart(show_obj.indexer_id)}

        if all([not need_images[self.POSTER],
                not need_images[self.BANNER],
                not need_images[self.POSTER_THUMB],
                not need_images[self.BANNER_THUMB],
                not need_images[self.FANART]]):
            sickrage.app.log.debug("No new cache images needed, not retrieving new ones")
            return

        # check the show dir for poster or banner images and use them
        if any([need_images[self.POSTER], need_images[self.BANNER], need_images[self.FANART]]):
            if os.path.isdir(show_obj.location):
                for cur_provider in sickrage.app.metadata_providers.values():
                    sickrage.app.log.debug(
                        "Checking if we can use the show image from the " + cur_provider.name + " metadata")
                    if os.path.isfile(cur_provider.get_poster_path(show_obj)):
                        cur_file_name = os.path.abspath(cur_provider.get_poster_path(show_obj))
                        cur_file_type = self.which_type(cur_file_name)

                        if cur_file_type is None:
                            sickrage.app.log.warning(
                                "Unable to retrieve image type {}, not using the image from {}".format(
                                    str(cur_file_type), cur_file_name))
                            continue

                        sickrage.app.log.debug("Checking if image " + cur_file_name + " (type " + str(
                            cur_file_type) + " needs metadata: " + str(need_images[cur_file_type]))

                        if cur_file_type in need_images and need_images[cur_file_type]:
                            sickrage.app.log.debug(
                                "Found an image in the show dir that doesn't exist in the cache, caching it: " + cur_file_name + ", type " + str(
                                    cur_file_type))
                            self._cache_image_from_file(cur_file_name, cur_file_type, show_obj.indexer_id)
                            need_images[cur_file_type] = False

        # download from indexer for missing ones
        for cur_image_type in [self.POSTER, self.BANNER, self.POSTER_THUMB, self.BANNER_THUMB, self.FANART]:
            sickrage.app.log.debug(
                "Seeing if we still need an image of type " + str(cur_image_type) + ": " + str(
                    need_images[cur_image_type]))
            if cur_image_type in need_images and need_images[cur_image_type]:
                self._cache_image_from_indexer(show_obj, cur_image_type, force)

        sickrage.app.log.info("Done cache check")
