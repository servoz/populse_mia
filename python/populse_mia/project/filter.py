##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

# Populse_MIA imports
from populse_mia import data_browser
from populse_mia.project import project


class Filter:
    """
    Class that represents a Filter, containing the results of both rapid and advanced search

    The advanced search creates a complex query to the database and is a combination of several "query lines" which
    are linked with AND or OR and all composed of:
    - A negation or not
    - A tag name or all visible tags
    - A condition (==, !=, >, <, >=, <=, CONTAINS, IN, BETWEEN)
    - A value

    Attributes:
        - nots: list of negations ("" or NOT)
        - values: list of values
        - fields: list of list of fields
        - links: list of links (AND/OR)
        - conditions: list of conditions (==, !=, <, >, <=, >=, IN, BETWEEN, CONTAINS, HAS VALUE, HAS NO VALUE)
        - search_bar: value in the rapid search bar
        - name: filter's name

    Methods:
        - json_format: returns the filter as a dictionary
        - generate_filter: apply the filter to the given list of scans
    """

    def __init__(self, name, nots, values, fields, links, conditions, search_bar):

        self.nots = nots
        self.values = values
        self.fields = fields
        self.links = links
        self.conditions = conditions
        self.search_bar = search_bar
        self.name = name

    def json_format(self):
        """
        Returns the filter as a dictionary

        :return: the filter as a dictionary
        """

        # Filter dictionary
        data = {
            "name": self.name,
            "search_bar_text": self.search_bar,
            "fields": self.fields,
            "conditions": self.conditions,
            "values": self.values,
            "links": self.links,
            "nots": self.nots
        }
        return data

    def generate_filter(self, current_project, scans, tags):
        """
        Apply the filter to the given list of scans

        :param current_project: Current project
        :param scans: List of scans to apply the filter into
        :param tags: List of tags to search in
        :return: The list of scans matching the filter
        """

        rapid_filter = data_browser.rapid_search.RapidSearch.prepare_filter(self.search_bar, tags, scans)
        rapid_result = current_project.session.filter_documents(project.COLLECTION_CURRENT, rapid_filter)
        rapid_list = [getattr(scan, project.TAG_FILENAME) for scan in rapid_result]
        advanced_filter = data_browser.advanced_search.AdvancedSearch.prepare_filters(self.links, self.fields,
                                                                                      self.conditions, self.values,
                                                                                      self.nots, rapid_list)
        advanced_result = current_project.session.filter_documents(project.COLLECTION_CURRENT, advanced_filter)
        final_result = [getattr(scan, project.TAG_FILENAME) for scan in advanced_result]
        return final_result
