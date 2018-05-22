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
