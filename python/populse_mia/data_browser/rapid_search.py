##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

# PyQt5 import
from PyQt5.QtWidgets import QLineEdit

# Populse_MIA imports
from populse_mia.project.project import TAG_FILENAME, TAG_BRICKS


class RapidSearch(QLineEdit):
    """
    Widget used to search for a pattern in the table (for all the visualized tags).

    Enter % to replace any string, _ to replace any character , *Not Defined* for the scans with missing value(s).
    Dates are in the following format: yyyy-mm-dd hh:mm:ss.fff”

    Attributes:
        - databrowser: parent data browser widget

    Methods:
        - prepare_not_defined_filter: prepares the rapid search filter for not defined values
        - prepare_filter: prepares the rapid search filter
    """

    def __init__(self, databrowser):

        super().__init__()

        self.databrowser = databrowser
        self.setPlaceholderText("Rapid search, enter % to replace any string, _ to replace any character ," +
                                " *Not Defined* for the scans with missing value(s),  " +
                                "dates are in the following format: yyyy-mm-dd hh:mm:ss.fff")

    def prepare_not_defined_filter(self, tags):
        """
        Prepares the rapid search filter for not defined values

        :param tags: list of tags to take into account
        :return: str filter corresponding to the rapid search for not defined values
        """

        query = ""

        or_to_write = False

        for tag in tags:

            if tag != TAG_BRICKS:

                if or_to_write:
                    query += " OR "

                query += "({" + tag + "} == null)"

                or_to_write = True

        query += " AND ({" + TAG_FILENAME + "} IN " + str(self.databrowser.table_data.scans_to_search).replace("'", "\"") + ")"

        query = "(" + query + ")"

        return query

    @staticmethod
    def prepare_filter(search, tags, scans):
        """
        Prepares the rapid search filter

        :param search: Search (str)
        :param tags: List of tags to take into account
        :param scans: List of scans to search into
        :return: str filter corresponding to the rapid search
        """

        query = ""

        or_to_write = False

        for tag in tags:

            if tag != TAG_BRICKS:

                if or_to_write:
                    query += " OR "

                query += "({" + tag + "} LIKE \"%" + search + "%\")"

                or_to_write = True

        query += " AND ({" + TAG_FILENAME + "} IN " + str(scans).replace("'", "\"") + ")"

        query = "(" + query + ")"

        return query
