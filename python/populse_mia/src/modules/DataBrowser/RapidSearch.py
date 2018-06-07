from PyQt5.QtWidgets import QLineEdit
from Project.Project import TAG_FILENAME

class RapidSearch(QLineEdit):

    def __init__(self, databrowser):

        super().__init__()

        self.databrowser = databrowser
        self.setPlaceholderText(
            "Rapid search, enter % to replace any string, _ to replace any character , *Not Defined* for the scans with missing value(s),  dates are in the following format: yyyy-mm-dd hh:mm:ss.fff")


    def prepare_not_defined_filter(self, tags):
        """
        Prepares the rapid search filter for not defined values
        :param tags: list of tags to take into account
        :return: str filter corresponding to the rapid search for not defined values
        """

        query = ""

        or_to_write = False

        for tag in tags:


            if or_to_write:
                query += " OR "

            query += "({" + tag + "} == null)"

            or_to_write = True

        query = "(" + query + ")"

        #print(query)

        return query

    def prepare_filter(self, search, tags):
        """
        Prepares the rapid search filter
        :param search: str search
        :param tags: list of tags to take into account
        :return: str filter corresponding to the rapid search
        """

        query = ""

        or_to_write = False

        for tag in tags:

            if or_to_write:
                query += " OR "

            query += "({" + tag + "} LIKE \"%" + search + "%\")"

            or_to_write = True

        query += " AND ({" + TAG_FILENAME + "} IN " + str(self.databrowser.table_data.scans_to_visualize).replace("'", "\"") + ")"

        query = "(" + query + ")"

        # print(query)

        return query