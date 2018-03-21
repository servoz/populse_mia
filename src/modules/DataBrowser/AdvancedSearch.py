from PyQt5.QtWidgets import QWidget, QGridLayout, QComboBox, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QObjectCleanupHandler
import os
from Utils.Tools import ClickableLabel

class AdvancedSearch(QWidget):

    def __init__(self, database, dataBrowser):
        """
        Class that manages the widget of the advanced search
        """

        super().__init__()

        self.database = database
        self.dataBrowser = dataBrowser
        self.rows = []

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
        if(len(self.rows) > 1):
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
        for tag in self.database.getVisualizedTags():
            fieldChoice.addItem(tag.tag)
        fieldChoice.addItem("All visualized tags")

        # Value choice
        conditionValue = QLineEdit()
        conditionValue.setObjectName('value')

        # Condition choice
        conditionChoice = QComboBox()
        conditionChoice.setObjectName('condition')
        conditionChoice.addItem("=")
        conditionChoice.addItem("!=")
        conditionChoice.addItem(">=")
        conditionChoice.addItem("<=")
        conditionChoice.addItem(">")
        conditionChoice.addItem("<")
        conditionChoice.addItem("BETWEEN")
        conditionChoice.addItem("IN")
        conditionChoice.addItem("CONTAINS")
        # Signal to update the placeholder text of the value
        conditionChoice.currentTextChanged.connect(lambda : self.displayValueRules(conditionChoice, conditionValue))

        # Minus to remove the row
        removeRowLabel = ClickableLabel()
        removeRowPicture = QPixmap(os.path.relpath(os.path.join("..", "sources_images", "red_minus.png")))
        removeRowPicture = removeRowPicture.scaledToHeight(30)
        removeRowLabel.setPixmap(removeRowPicture)

        # Everything appended to the row
        rowLayout.append(None) # Link room
        rowLayout.append(notChoice)
        rowLayout.append(fieldChoice)
        rowLayout.append(conditionChoice)
        rowLayout.append(conditionValue)
        rowLayout.append(removeRowLabel)
        rowLayout.append(None) # Add row room

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
        if(choice.currentText() == "BETWEEN"):
            value.setPlaceholderText("Please separate the two inclusive borders of the range by a comma and a space")
        elif (choice.currentText() == "IN"):
            value.setPlaceholderText("Please separate each list item by a comma and a space")
        else:
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
                if(widget != None):
                    main_layout.addWidget(widget, i, j)
                j = j + 1
            i = i + 1

        #Search button added at the end
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
            if (self.rows[i][6] != None):
                self.rows[i][6].setParent(None)
                self.rows[i][6].deleteLater()
                self.rows[i][6] = None
            # Link removed from every row
            if (self.rows[i][0] != None):
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
            if(widget in row):
                return True
        return False

    def launch_search(self):
        """
        Called to start the search
        """

        (fields, conditions, values, links, nots) = self.get_filters() # Filters gotten

        # Result gotten
        result = self.database.getScansAdvancedSearch(links, fields, conditions, values, nots)
        # DataBrowser updated with the new selection
        self.dataBrowser.table_data.scans_to_visualize = result
        self.dataBrowser.table_data.update_table()

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
                    if (childName == 'link'):
                        links.append(child.currentText())
                    elif (childName == 'condition'):
                        conditions.append(child.currentText())
                    elif (childName == 'field'):
                        fields.append(child.currentText())
                    elif (childName == 'value'):
                        values.append(child.displayText())
                    elif (childName == 'not'):
                        nots.append(child.currentText())
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
            row[2].setCurrentText(fields[i])
            row[3].setCurrentText(conditions[i])
            row[4].setText(values[i])
            i += 1

        # Result gotten
        result = self.database.getScansAdvancedSearch(links, fields, conditions, values, nots)
        # DataBrowser updated with the new selection
        self.dataBrowser.table_data.scans_to_visualize = result
        self.dataBrowser.table_data.update_table()