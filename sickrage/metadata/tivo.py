# Author: echel0n <echel0n@sickrage.ca>
# URL: https://sickrage.ca
#
# This file is part of SickRage.
#
# SickRage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SickRage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SickRage.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import datetime
import io
import os

import sickrage
from sickrage.core.exceptions import ShowNotFoundException
from sickrage.core.helpers import chmodAsParent
from sickrage.indexers import srIndexerApi
from sickrage.indexers.exceptions import indexer_episodenotfound, \
    indexer_error, indexer_seasonnotfound, indexer_shownotfound
from sickrage.metadata import GenericMetadata


class TIVOMetadata(GenericMetadata):
    """
    Metadata generation class for TIVO

    The following file structure is used:

    show_root/Season ##/filename.ext            (*)
    show_root/Season ##/.meta/filename.ext.txt  (episode metadata)

    This class only generates episode specific metadata files, it does NOT generate a default.txt file.
    """

    def __init__(self,
                 show_metadata=False,
                 episode_metadata=False,
                 fanart=False,
                 poster=False,
                 banner=False,
                 episode_thumbnails=False,
                 season_posters=False,
                 season_banners=False,
                 season_all_poster=False,
                 season_all_banner=False):

        GenericMetadata.__init__(self,
                                 show_metadata,
                                 episode_metadata,
                                 fanart,
                                 poster,
                                 banner,
                                 episode_thumbnails,
                                 season_posters,
                                 season_banners,
                                 season_all_poster,
                                 season_all_banner)

        self.name = 'TIVO'

        self._ep_nfo_extension = "txt"

        # web-ui metadata template
        self.eg_show_metadata = "<i>not supported</i>"
        self.eg_episode_metadata = "Season##\\.meta\\<i>filename</i>.ext.txt"
        self.eg_fanart = "<i>not supported</i>"
        self.eg_poster = "<i>not supported</i>"
        self.eg_banner = "<i>not supported</i>"
        self.eg_episode_thumbnails = "<i>not supported</i>"
        self.eg_season_posters = "<i>not supported</i>"
        self.eg_season_banners = "<i>not supported</i>"
        self.eg_season_all_poster = "<i>not supported</i>"
        self.eg_season_all_banner = "<i>not supported</i>"

    # Override with empty methods for unsupported features
    def retrieveShowMetadata(self, folder):
        # no show metadata generated, we abort this lookup function
        return None, None, None

    def create_show_metadata(self, show_obj):
        pass

    def update_show_indexer_metadata(self, show_obj):
        pass

    def get_show_file_path(self, show_obj):
        pass

    def create_fanart(self, show_obj):
        pass

    def create_poster(self, show_obj):
        pass

    def create_banner(self, show_obj):
        pass

    def create_episode_thumb(self, ep_obj):
        pass

    @staticmethod
    def get_episode_thumb_path(ep_obj):
        pass

    def create_season_posters(self, ep_obj):
        pass

    def create_season_banners(self, ep_obj):
        pass

    def create_season_all_poster(self, show_obj):
        pass

    def create_season_all_banner(self, show_obj):
        pass

    # Override generic class
    def get_episode_file_path(self, ep_obj):
        """
        Returns a full show dir/.meta/episode.txt path for Tivo
        episode metadata files.

        Note, that pyTivo requires the metadata filename to include the original extention.

        ie If the episode name is foo.avi, the metadata name is foo.avi.txt

        ep_obj: a TVEpisode object to get the path for
        """
        if os.path.isfile(ep_obj.location):
            metadata_file_name = os.path.basename(ep_obj.location) + "." + self._ep_nfo_extension
            metadata_dir_name = os.path.join(os.path.dirname(ep_obj.location), '.meta')
            metadata_file_path = os.path.join(metadata_dir_name, metadata_file_name)
        else:
            sickrage.app.log.debug("Episode location doesn't exist: " + str(ep_obj.location))
            return ''
        return metadata_file_path

    def _ep_data(self, ep_obj):
        """
        Creates a key value structure for a Tivo episode metadata file and
        returns the resulting data object.

        ep_obj: a TVEpisode instance to create the metadata file for.

        Lookup the show in http://thetvdb.com/ using the python library:

        https://github.com/dbr/indexer_api/

        The results are saved in the object myShow.

        The key values for the tivo metadata file are from:

        http://pytivo.sourceforge.net/wiki/index.php/Metadata
        """

        data = ""

        eps_to_write = [ep_obj] + ep_obj.relatedEps

        indexer_lang = ep_obj.show.lang or sickrage.app.config.INDEXER_DEFAULT_LANGUAGE

        try:
            lINDEXER_API_PARMS = srIndexerApi(ep_obj.show.indexer).api_params.copy()

            lINDEXER_API_PARMS['language'] = indexer_lang

            if ep_obj.show.dvdorder != 0:
                lINDEXER_API_PARMS['dvdorder'] = True

            t = srIndexerApi(ep_obj.show.indexer).indexer(**lINDEXER_API_PARMS)
            myShow = t[ep_obj.show.indexerid]
        except indexer_shownotfound as e:
            raise ShowNotFoundException(str(e))
        except indexer_error as e:
            sickrage.app.log.error("Unable to connect to " + srIndexerApi(
                ep_obj.show.indexer).name + " while creating meta files - skipping - " + str(e))
            return False

        for curEpToWrite in eps_to_write:

            try:
                myEp = myShow[curEpToWrite.season][curEpToWrite.episode]
            except (indexer_episodenotfound, indexer_seasonnotfound):
                sickrage.app.log.info(
                    "Unable to find episode %dx%d on %s, has it been removed? Should I delete from db?" % (
                    curEpToWrite.season, curEpToWrite.episode, srIndexerApi(ep_obj.show.indexer).name))
                return None

            if ep_obj.season == 0 and not getattr(myEp, 'firstaired', None):
                myEp["firstaired"] = str(datetime.date.fromordinal(1))

            if not (getattr(myEp, 'episodename', None) and getattr(myEp, 'firstaired', None)):
                return None

            if getattr(myShow, 'seriesname', None):
                data += ("title : " + myShow["seriesname"] + "\n")
                data += ("seriesTitle : " + myShow["seriesname"] + "\n")

            data += ("episodeTitle : " + curEpToWrite._format_pattern('%Sx%0E %EN') + "\n")

            # This should be entered for episodic shows and omitted for movies. The standard tivo format is to enter
            # the season number followed by the episode number for that season. For example, enter 201 for season 2
            # episode 01.

            # This only shows up if you go into the Details from the Program screen.

            # This seems to disappear once the video is transferred to TiVo.

            # NOTE: May not be correct format, missing season, but based on description from wiki leaving as is.
            data += ("episodeNumber : " + str(curEpToWrite.episode) + "\n")

            # Must be entered as true or false. If true, the year from originalAirDate will be shown in parentheses
            # after the episode's title and before the description on the Program screen.

            # FIXME: Hardcode isEpisode to true for now, not sure how to handle movies
            data += "isEpisode : true\n"

            # Write the synopsis of the video here
            # Micrsoft Word's smartquotes can die in a fire.
            sanitizedDescription = curEpToWrite.description
            # Replace double curly quotes
            sanitizedDescription = sanitizedDescription.replace("\u201c", "\"").replace("\u201d", "\"")
            # Replace single curly quotes
            sanitizedDescription = sanitizedDescription.replace("\u2018", "'").replace("\u2019", "'").replace("\u02BC",
                                                                                                              "'")

            data += ("description : " + sanitizedDescription + "\n")

            # Usually starts with "SH" and followed by 6-8 digits.
            # Tivo uses zap2it for thier data, so the series id is the zap2it_id.
            if getattr(myShow, 'zap2it_id', None):
                data += ("seriesId : " + myShow["zap2it_id"] + "\n")

            # This is the call sign of the channel the episode was recorded from.
            if getattr(myShow, 'network', None):
                data += ("callsign : " + myShow["network"] + "\n")

            # This must be entered as yyyy-mm-ddThh:mm:ssZ (the t is capitalized and never changes, the Z is also
            # capitalized and never changes). This is the original air date of the episode.
            # NOTE: Hard coded the time to T00:00:00Z as we really don't know when during the day the first run happened.
            if curEpToWrite.airdate != datetime.date.fromordinal(1):
                data += ("originalAirDate : " + str(curEpToWrite.airdate) + "T00:00:00Z\n")

            # This shows up at the beginning of the description on the Program screen and on the Details screen.
            for actor in t.actors(int(ep_obj.show.indexerid)):
                if 'name' in actor and actor['name'].strip():
                    data += ("vActor : " + actor['name'].strip() + "\n")

            # This is shown on both the Program screen and the Details screen.
            if getattr(myEp, 'rating', None):
                try:
                    rating = float(myEp['rating'])
                except ValueError:
                    rating = 0.0
                # convert 10 to 4 star rating. 4 * rating / 10
                # only whole numbers or half numbers work. multiply by 2, round, divide by 2.0
                rating = round(8 * rating / 10) / 2.0
                data += ("starRating : " + str(rating) + "\n")

            # This is shown on both the Program screen and the Details screen.
            # It uses the standard TV rating system of: TV-Y7, TV-Y, TV-G, TV-PG, TV-14, TV-MA and TV-NR.
            if getattr(myShow, 'contentrating', None):
                data += ("tvRating : " + str(myShow["contentrating"]) + "\n")

            # This field can be repeated as many times as necessary or omitted completely.
            if ep_obj.show.genre:
                for genre in ep_obj.show.genre.split('|'):
                    if genre:
                        data += ("vProgramGenre : " + str(genre) + "\n")

                        # NOTE: The following are metadata keywords are not used
                        # displayMajorNumber
                        # showingBits
                        # displayMinorNumber
                        # colorCode
                        # vSeriesGenre
                        # vGuestStar, vDirector, vExecProducer, vProducer, vWriter, vHost, vChoreographer
                        # partCount
                        # partIndex

        return data

    def write_ep_file(self, ep_obj):
        """
        Generates and writes ep_obj's metadata under the given path with the
        given filename root. Uses the episode's name with the extension in
        _ep_nfo_extension.

        ep_obj: TVEpisode object for which to create the metadata

        file_name_path: The file name to use for this metadata. Note that the extension
                will be automatically added based on _ep_nfo_extension. This should
                include an absolute path.
        """
        data = self._ep_data(ep_obj)

        if not data:
            return False

        nfo_file_path = self.get_episode_file_path(ep_obj)
        nfo_file_dir = os.path.dirname(nfo_file_path)

        try:
            if not os.path.isdir(nfo_file_dir):
                sickrage.app.log.debug("Metadata dir didn't exist, creating it at " + nfo_file_dir)
                os.makedirs(nfo_file_dir)
                chmodAsParent(nfo_file_dir)

            sickrage.app.log.debug("Writing episode nfo file to " + nfo_file_path)

            with io.open(nfo_file_path, 'w') as nfo_file:
                # Calling encode directly, b/c often descriptions have wonky characters.
                nfo_file.write(data.encode("utf-8"))

            chmodAsParent(nfo_file_path)

        except EnvironmentError as e:
            sickrage.app.log.error(
                "Unable to write file to " + nfo_file_path + " - are you sure the folder is writable? {}".format(
                    e.message))
            return False

        return True
