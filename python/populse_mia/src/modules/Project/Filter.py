import DataBrowser
import Project


class Filter:
    """
    Class that represents a Filter
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

    def generate_filter(self, project, scans, tags):
        """
        Apply the filter to the list of scans given
        :param project: Current project
        :param scans: List of scans to apply the filter into
        :param tags: List of tags to search in
        :return: The list of scans matching the filter
        """

        rapid_filter = DataBrowser.RapidSearch.RapidSearch.prepare_filter(self.search_bar, tags, scans)
        rapid_result = project.session.filter_documents(Project.Project.COLLECTION_CURRENT, rapid_filter)
        rapid_list = [getattr(scan, Project.Project.TAG_FILENAME) for scan in rapid_result]
        advanced_filter = DataBrowser.AdvancedSearch.AdvancedSearch.prepare_filters(self.links, self.fields, self.conditions, self.values, self.nots, rapid_list)
        advanced_result = project.session.filter_documents(Project.Project.COLLECTION_CURRENT, advanced_filter)
        final_result = [getattr(scan, Project.Project.TAG_FILENAME) for scan in advanced_result]
        return final_result