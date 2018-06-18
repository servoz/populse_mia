import os

from PyQt5.QtCore import QObjectCleanupHandler, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QGridLayout, QComboBox, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox

from Utils.Tools import ClickableLabel

from Project.Project import TAG_FILENAME, COLLECTION_CURRENT

import populse_db

class AdvancedSearch(QWidget):

    def __init__(self, project, dataBrowser, scans_list=[], tags_list=[]):
        """
        Class that manages the widget of the advanced search
        """

        super().__init__()

        self.project = project
        self.dataBrowser = dataBrowser
        self.rows = []
        self.scans_list = scans_list
        self.tags_list = tags_list

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
        if len(self.tags_list) > 0:
            for tag in self.tags_list:
                fieldChoice.addItem(tag)
        else:
            for tag in self.project.session.get_visibles():
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
        conditionChoice.model().sort(0)

        # Signal to update the placeholder text of the value
        conditionChoice.currentTextChanged.connect(lambda: self.displayValueRules(conditionChoice, conditionValue))

        # Signal to update the list of conditions, depending on the tag type
        fieldChoice.currentTextChanged.connect(lambda: self.displayConditionRules(fieldChoice, conditionChoice))

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

        self.displayConditionRules(fieldChoice, conditionChoice)

    def displayConditionRules(self, field, condition):
        """
        Sets the list of condition choices, depending on the tag type
        :param field: field
        :param condition: condition
        """

        tag_name = field.currentText()
        tag_row = self.project.session.get_field(COLLECTION_CURRENT, tag_name)

        no_operators_tags = []
        for list_type in populse_db.database.LIST_TYPES:
            no_operators_tags.append(list_type)
        no_operators_tags.append(populse_db.database.FIELD_TYPE_STRING)
        no_operators_tags.append(populse_db.database.FIELD_TYPE_BOOLEAN)

        if tag_row is not None and tag_row.type in no_operators_tags:
            condition.removeItem(condition.findText("<"))
            condition.removeItem(condition.findText(">"))
            condition.removeItem(condition.findText("<="))
            condition.removeItem(condition.findText(">="))
            condition.removeItem(condition.findText("BETWEEN"))

        if tag_row is not None and tag_row.type in populse_db.database.LIST_TYPES:
            condition.removeItem(condition.findText("IN"))

        if tag_row is None or tag_row.type not in no_operators_tags:
            operators_to_reput = ["<", ">", "<=", ">=", "BETWEEN"]
            for operator in operators_to_reput:
                is_op_existing = condition.findText(operator) != -1
                if not is_op_existing:
                    condition.addItem(operator)

        if tag_row is None or tag_row.type not in populse_db.database.LIST_TYPES:
            operators_to_reput = ["IN"]
            for operator in operators_to_reput:
                is_op_existing = condition.findText(operator) != -1
                if not is_op_existing:
                    condition.addItem(operator)

        condition.model().sort(0)

    def displayValueRules(self, choice, value):
        """
        Called when the condition choice is changed, to update the placeholder text
        :param choice: choice
        :param value: value
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
        (fields, conditions, values, links, nots) = self.get_filters(False)

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
        for i in range (0, len(self.rows)):
            for j in range(0, 7):
                widget = self.rows[i][j]
                if widget != None:
                    main_layout.addWidget(widget, i, j)

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
        for i in range (0, len(self.rows)):
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
        for i in range (1, len(self.rows)):
            row = self.rows[i]
            linkChoice = QComboBox()
            linkChoice.setObjectName('link')
            linkChoice.addItem("AND")
            linkChoice.addItem("OR")
            if len(links) >= i:
                linkChoice.setCurrentText(links[i - 1])
            row[0] = linkChoice

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

        (fields, conditions, values, links, nots) = self.get_filters(True)  # Filters gotten

        old_scans_list = self.dataBrowser.table_data.scans_to_visualize

        # Result gotten
        try:

            filter_query = self.prepare_filters(links, fields, conditions, values, nots, self.scans_list)
            result = self.project.session.filter_documents(COLLECTION_CURRENT, filter_query)

            # DataBrowser updated with the new selection
            result_names = [getattr(document, TAG_FILENAME) for document in result]

            self.project.currentFilter.nots = nots
            self.project.currentFilter.values = values
            self.project.currentFilter.fields = fields
            self.project.currentFilter.links = links
            self.project.currentFilter.conditions = conditions

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

        #print(result_names)

        self.dataBrowser.table_data.scans_to_visualize = result_names
        self.dataBrowser.table_data.scans_to_search = result_names
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
                elif row_condition == "CONTAINS":
                    row_field_query = "({" + row_field + "} LIKE \"%" + row_value + "%\")"
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
        final_query += " AND ({" + TAG_FILENAME + "} IN " + str(scans).replace("'", "\"") + ")"

        final_query = "(" + final_query + ")"

        #print(final_query)

        return final_query

    def get_filters(self, replace_all_by_fields):
        """
        To get the filters in list form
        :param replace_all_by_fields: to replace All visualized tags by the list of visible fields
        :return: Lists of filters (fields, conditions, values, links, nots)
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
                            if replace_all_by_fields:
                                fields.append(self.project.database.get_visibles())
                            else:
                                fields.append([child.currentText()])
                    elif childName == 'value':
                        values.append(child.displayText())
                    elif childName == 'not':
                        nots.append(child.currentText())

        operators = ["<", ">", "<=", ">=", "BETWEEN"]
        no_operators_tags = []
        for list_type in populse_db.database.LIST_TYPES:
            no_operators_tags.append(list_type)
        no_operators_tags.append(populse_db.database.FIELD_TYPE_STRING)
        no_operators_tags.append(populse_db.database.FIELD_TYPE_BOOLEAN)

        # Converting BETWEEN and IN values into lists
        for i in range(0, len(conditions)):
            if conditions[i] == "BETWEEN" or conditions[i] == "IN":
                values[i] = values[i].split("; ")
            if conditions[i] == "IN":
                for tag in fields[i].copy():
                    tag_row = self.project.database.get_field(COLLECTION_CURRENT, tag)
                    if tag_row.type in populse_db.database.LIST_TYPES:
                        fields[i].remove(tag)
            elif conditions[i] in operators:
                for tag in fields[i].copy():
                    tag_row = self.project.database.get_field(COLLECTION_CURRENT, tag)
                    if tag_row.type in no_operators_tags:
                        fields[i].remove(tag)

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

        for i in range (0, len(nots)):
            self.add_row()
            row = self.rows[i]
            if i > 0:
                row[0].setCurrentText(links[i - 1])
            row[1].setCurrentText(nots[i])
            row[2].setCurrentText(fields[i][0])

            # Replacing all visualized tags by the current list of visible tags
            if fields[i][0] == "All visualized tags":
                fields[i] = self.project.database.get_visibles()

            row[3].setCurrentText(conditions[i])
            row[4].setText(str(values[i]))

        old_rows = self.dataBrowser.table_data.scans_to_visualize

        # Filter applied only if at least one row
        if len(nots) > 0:
            # Result gotten
            try:

                filter_query = self.prepare_filters(links, fields, conditions, values, nots, self.scans_list)
                result = self.project.session.filter_documents(COLLECTION_CURRENT, filter_query)

                # DataBrowser updated with the new selection
                result_names = [getattr(document, TAG_FILENAME) for document in result]

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

            # DataBrowser updated with the new selection
            self.dataBrowser.table_data.scans_to_visualize = result_names

        # Otherwise, all the scans are reput
        else:
            # DataBrowser updated with every scan
            if self.scans_list:
                self.dataBrowser.table_data.scans_to_visualize = self.scans_list
            else:
                self.dataBrowser.table_data.scans_to_visualize = \
                    self.project.database.get_documents_names(COLLECTION_CURRENT)

        self.dataBrowser.table_data.update_visualized_rows(old_rows)
