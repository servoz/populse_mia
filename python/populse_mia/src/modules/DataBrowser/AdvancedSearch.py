import os

from PyQt5.QtCore import QObjectCleanupHandler
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QGridLayout, QComboBox, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox

from Utils.Tools import ClickableLabel

from populse_db.database_model import DOCUMENT_PRIMARY_KEY

class AdvancedSearch(QWidget):

    def __init__(self, project, dataBrowser, scans_list=[]):
        """
        Class that manages the widget of the advanced search
        """

        super().__init__()

        self.project = project
        self.dataBrowser = dataBrowser
        self.rows = []
        self.scans_list = scans_list

    def show_search(self):
        """
        Called when the Advanced Search button is clicked, we reset the rows
        """
        self.rows = []
        self.add_row()

    def remove_row(self, rowLayout):
        """
        Called when a row must be removed
        :param rowLayout: Row to remove
        """

        # We remove the row only if there is at least 2 rows, because we always must keep at least one
        if (len(self.rows) > 1):
            self.rows.remove(rowLayout)

        # We refresh the view
        self.refresh_search()

    def add_row(self):
        """
        Called when a row must be added
        """

        rowLayout = []

        # NOT choice
        notChoice = QComboBox()
        notChoice.setObjectName('not')
        notChoice.addItem("")
        notChoice.addItem("NOT")

        # Field choice
        fieldChoice = QComboBox()
        fieldChoice.setObjectName('field')
        for tag in self.project.getVisibles():
            fieldChoice.addItem(tag)
        fieldChoice.model().sort(0)
        fieldChoice.addItem("All visualized tags")

        # Value choice
        conditionValue = QLineEdit()
        conditionValue.setObjectName('value')

        # Condition choice
        conditionChoice = QComboBox()
        conditionChoice.setObjectName('condition')
        conditionChoice.addItem("==")
        conditionChoice.addItem("!=")
        conditionChoice.addItem(">=")
        conditionChoice.addItem("<=")
        conditionChoice.addItem(">")
        conditionChoice.addItem("<")
        conditionChoice.addItem("BETWEEN")
        conditionChoice.addItem("IN")
        conditionChoice.addItem("CONTAINS")
        conditionChoice.addItem("HAS VALUE")
        conditionChoice.addItem("HAS NO VALUE")
        # Signal to update the placeholder text of the value
        conditionChoice.currentTextChanged.connect(lambda: self.displayValueRules(conditionChoice, conditionValue))

        # Minus to remove the row
        removeRowLabel = ClickableLabel()
        removeRowPicture = QPixmap(os.path.relpath(os.path.join("..", "sources_images", "red_minus.png")))
        removeRowPicture = removeRowPicture.scaledToHeight(30)
        removeRowLabel.setPixmap(removeRowPicture)

        # Everything appended to the row
        rowLayout.append(None)  # Link room
        rowLayout.append(notChoice)
        rowLayout.append(fieldChoice)
        rowLayout.append(conditionChoice)
        rowLayout.append(conditionValue)
        rowLayout.append(removeRowLabel)
        rowLayout.append(None)  # Add row room

        # Signal to remove the row
        removeRowLabel.clicked.connect(lambda: self.remove_row(rowLayout))

        self.rows.append(rowLayout)

        self.refresh_search()

    def displayValueRules(self, choice, value):
        """
        Called when the condition choice is changed, to update the placeholder text
        :param choice:
        :param value:
        :return:
        """
        if choice.currentText() == "BETWEEN":
            value.setDisabled(False)
            value.setPlaceholderText(
                "Please separate the two inclusive borders of the range by a semicolon and a space")
        elif choice.currentText() == "IN":
            value.setDisabled(False)
            value.setPlaceholderText("Please separate each list item by a semicolon and a space")
        elif choice.currentText() == "HAS VALUE" or choice.currentText() == "HAS NO VALUE":
            value.setDisabled(True)
            value.setPlaceholderText("")
            value.setText("")
        else:
            value.setDisabled(False)
            value.setPlaceholderText("")

    def refresh_search(self):
        """
        Called to refresh the advanced search
        """

        # Old values stored
        (fields, conditions, values, links, nots) = self.get_filters()

        # We remove the old layout
        self.clearLayout(self.layout())
        QObjectCleanupHandler().add(self.layout())

        # Links and add rows removed from every row
        self.rows_borders_removed()

        # Links and add rows reput in the good rows
        self.rows_borders_added(links)

        master_layout = QVBoxLayout()
        main_layout = QGridLayout()

        # Everything added to the layout
        i = 0
        while i < len(self.rows):
            j = 0
            while j < 7:
                widget = self.rows[i][j]
                if widget != None:
                    main_layout.addWidget(widget, i, j)
                j = j + 1
            i = i + 1

        # Search button added at the end
        searchLayout = QHBoxLayout(None)
        searchLayout.setObjectName("search layout")
        search = QPushButton("Search")
        search.setFixedWidth(100)
        search.clicked.connect(self.launch_search)
        searchLayout.addWidget(search)
        searchLayout.setParent(None)

        # New layout added
        master_layout.addLayout(main_layout)
        master_layout.addLayout(searchLayout)
        self.setLayout(master_layout)

    def rows_borders_removed(self):
        """
        Link and add row removed from every row
        """

        # We remove all the links and the add rows
        i = 0
        while i < len(self.rows):
            # Plus removed from every row
            if self.rows[i][6] != None:
                self.rows[i][6].setParent(None)
                self.rows[i][6].deleteLater()
                self.rows[i][6] = None
            # Link removed from every row
            if self.rows[i][0] != None:
                self.rows[i][0].setParent(None)
                self.rows[i][0].deleteLater()
                self.rows[i][0] = None
            i = i + 1

    def rows_borders_added(self, links):
        """
        Adds the links and the add row to the good rows
        :param links: Old links to reput
        """

        # Plus added to the last row
        addRowLabel = ClickableLabel()
        addRowLabel.setObjectName('plus')
        addRowPicture = QPixmap(os.path.relpath(os.path.join("..", "sources_images", "green_plus.png")))
        addRowPicture = addRowPicture.scaledToHeight(20)
        addRowLabel.setPixmap(addRowPicture)
        addRowLabel.clicked.connect(self.add_row)
        self.rows[len(self.rows) - 1][6] = addRowLabel

        # Link added to every row, except the first one
        i = 1
        while i < len(self.rows):
            row = self.rows[i]
            linkChoice = QComboBox()
            linkChoice.setObjectName('link')
            linkChoice.addItem("AND")
            linkChoice.addItem("OR")
            if len(links) >= i:
                linkChoice.setCurrentText(links[i - 1])
            row[0] = linkChoice
            i = i + 1

    def clearLayout(self, layout):
        """
        Called to clear a layout
        :param layout: layout to clear
        """
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                # We clear the widget only if the row does not exist anymore
                if widget is not None and not self.rowsContainsWidget(widget):
                    pass
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def rowsContainsWidget(self, widget):
        """
        To know if the widget is still used
        :param widget: Widget to check
        """
        for row in self.rows:
            if (widget in row):
                return True
        return False

    def launch_search(self):
        """
        Called to start the search
        """

        (fields, conditions, values, links, nots) = self.get_filters()  # Filters gotten

        old_scans_list = self.dataBrowser.table_data.scans_to_visualize

        # Result gotten
        try:
            filter_query = self.prepare_filters(links, fields, conditions, values, nots, self.scans_list)
            result = self.project.database.filter_documents(filter_query)

            # DataBrowser updated with the new selection
            result_names = []
            for document in result:
                result_names.append(getattr(document, DOCUMENT_PRIMARY_KEY))

        except Exception as e:
            print(e)

            # Error message if the search can't be done, and visualization of all scans in the databrowser
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText(
                "Error in the search")
            msg.setInformativeText(
                "The search has encountered a problem, you can correct it and launch it again.")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.buttonClicked.connect(msg.close)
            msg.exec()
            result_names = self.scans_list

        self.dataBrowser.table_data.scans_to_visualize = result_names
        self.dataBrowser.table_data.update_visualized_rows(old_scans_list)

    def prepare_filters(self, links, fields, conditions, values, nots, scans):
        """
        Prepares the str representation of the filter
        :param links: list of links (AND/OR)
        :param fields: list of list of fields
        :param conditions: list of conditions (==, !=, <, >, <=, >=, IN, BETWEEN, CONTAINS, HAS VALUE, HAS NO VALUE)
        :param values: list of values
        :param nots: list of negations ("" or NOT)
        :param scans: list of scans to search in
        :return: str representation of the filter
        """

        row_queries = []
        final_query = ""

        # For each row of constraint
        for row in range(0, len(fields)):
            row_fields = fields[row]
            row_condition = conditions[row]
            row_value = values[row]
            row_not = nots[row]

            row_query = "("

            or_to_write = False
            for row_field in row_fields:
                if row_condition == "IN":
                    row_field_query = "({" + row_field + "} " + row_condition + " " + str(row_value).replace("'", "\"") + ")"
                elif row_condition == "BETWEEN":
                    row_field_query = "(({" + row_field + "} >= \"" + row_value[0] + "\") AND (" + row_field + " <= \"" + row_value[1] + "\"))"
                elif row_condition == "HAS VALUE":
                    row_field_query = "({" + row_field + "} != null)"
                elif row_condition == "HAS NO VALUE":
                    row_field_query = "({" + row_field + "} == null)"
                else:
                    row_field_query = "({" + row_field + "} " + row_condition + " \"" + row_value + "\")"

                # Putting OR between conditions if several tags to search in
                if or_to_write:
                    row_field_query = " OR " + row_field_query

                or_to_write = True

                row_query += row_field_query

            row_query += ")"
            row_queries.append(row_query)

            # Negation added if needed
            if row_not == "NOT":
                row_queries[row]  = "(NOT " + row_queries[row] + ")"

        final_query += row_queries[0]

        # Putting the link between each row
        for row in range(0, len(links)):
            link = links[row]
            final_query += " " + link + " " + row_queries[row + 1]

        # Taking into account the list of scans
        final_query += " AND ({" + DOCUMENT_PRIMARY_KEY + "} IN " + str(scans).replace("'", "\"") + ")"

        final_query = "(" + final_query + ")"

        return final_query

    def get_filters(self):
        """
        To get the filters in list form
        :return: Lists of filters
        """

        # Lists to get all the data of the search
        fields = []
        conditions = []
        values = []
        links = []
        nots = []
        for row in self.rows:
            for widget in row:
                if widget != None:
                    child = widget
                    childName = child.objectName()
                    if childName == 'link':
                        links.append(child.currentText())
                    elif childName == 'condition':
                        conditions.append(child.currentText())
                    elif childName == 'field':
                        if child.currentText() != "All visualized tags":
                            fields.append([child.currentText()])
                        else:
                            tags = self.project.getVisibles()
                            fields.append(tags)
                    elif childName == 'value':
                        values.append(child.displayText())
                    elif childName == 'not':
                        nots.append(child.currentText())

        # Converting BETWEEN and IN values into lists
        for i in range(0, len(conditions)):
            if conditions[i] == "BETWEEN" or conditions[i] == "IN":
                values[i] = values[i].split("; ")

        return fields, conditions, values, links, nots

    def apply_filter(self, filter):
        """
        To apply an open filter
        :param filter: Filter object opened to apply
        :return:
        """
        self.rows = []

        # Data
        nots = filter.nots
        values = filter.values
        conditions = filter.conditions
        links = filter.links
        fields = filter.fields

        i = 0
        while i < len(nots):
            self.add_row()
            row = self.rows[i]
            if i > 0:
                row[0].setCurrentText(links[i - 1])
            row[1].setCurrentText(nots[i])
            if len(fields[i]) > 1:
                row[2].setCurrentText("All visualized tags")
            else:
                row[2].setCurrentText(fields[i][0])
            row[3].setCurrentText(conditions[i])
            row[4].setText(str(values[i]))
            i += 1

        old_rows = self.dataBrowser.table_data.scans_to_visualize

        # Filter applied only if at least one row
        if len(nots) > 0:
            # Result gotten
            result = self.project.database.get_documents_matching_advanced_search(links, fields, conditions,
                                                                                  values, nots, self.scans_list)
            # DataBrowser updated with the new selection
            self.dataBrowser.table_data.scans_to_visualize = result

        # Otherwise, we reput all the scans
        else:
            # DataBrowser updated with every scan
            if self.scans_list:
                self.dataBrowser.table_data.scans_to_visualize = self.scans_list
            else:
                self.dataBrowser.table_data.scans_to_visualize = self.project.database.get_documents_names()

        self.dataBrowser.table_data.update_visualized_rows(old_rows)
