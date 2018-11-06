##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

from sqlalchemy import create_engine, MetaData, String, Boolean, Integer, Enum, Column, Table
from sqlalchemy.exc import ArgumentError
from sqlalchemy.schema import CreateTable
from sqlalchemy.orm import mapper

# Populse_db imports
from populse_db.database import Database, FIELD_TABLE, FIELD_TYPE_STRING, FIELD_TYPE_DATE, FIELD_TYPE_LIST_STRING, \
    FIELD_TYPE_LIST_FLOAT, FIELD_TYPE_LIST_DATETIME, FIELD_TYPE_LIST_TIME, FIELD_TYPE_LIST_DATE, \
    FIELD_TYPE_LIST_INTEGER, FIELD_TYPE_DATETIME, FIELD_TYPE_INTEGER, FIELD_TYPE_FLOAT, FIELD_TYPE_TIME, \
    FIELD_TYPE_BOOLEAN, FIELD_TYPE_LIST_BOOLEAN, FIELD_TYPE_JSON, FIELD_TYPE_LIST_JSON, COLLECTION_TABLE, \
    DatabaseSession, ALL_TYPES, LIST_TYPES, TYPE_TO_COLUMN
from populse_db.filter import QUERY_MIXED

TAG_ORIGIN_BUILTIN = "builtin"
TAG_ORIGIN_USER = "user"

# Tag unit
TAG_UNIT_MS = "ms"
TAG_UNIT_MM = "mm"
TAG_UNIT_DEGREE = "degree"
TAG_UNIT_HZPIXEL = "Hz/pixel"
TAG_UNIT_MHZ = "MHz"

ALL_UNITS = [TAG_UNIT_MS, TAG_UNIT_MM,
             TAG_UNIT_DEGREE, TAG_UNIT_HZPIXEL, TAG_UNIT_MHZ]


class DatabaseMIA(Database):
    """
    Class overriding the default behavior of populse_db

    Methods:
        - _Database__create_empty_schema: overrides the method creating the empty schema
        - __enter__: returns a DatabaseSession instance for using the database
        - __exit__: releases a DatabaseSession previously created by __enter__
    """

    def __init__(self, string_engine):

        super().__init__(string_engine, caches=True, list_tables=True, query_type=QUERY_MIXED)

    def _Database__create_empty_schema(self, string_engine):
        """
        Overrides the method creating the empty schema, in order to add columns to field table

        :param string_engine: Path of the new database file
        """

        try:
            if string_engine.startswith('sqlite'):
                engine = create_engine(string_engine, connect_args={'check_same_thread': False})
            else:
                engine = create_engine(string_engine)
        except ArgumentError:
            raise ValueError("The string engine is invalid, please refer to the documentation for more "
                             "details on how to write the string engine")
        metadata = MetaData()
        metadata.reflect(bind=engine)
        if FIELD_TABLE in metadata.tables and COLLECTION_TABLE in metadata.tables:
            return engine
        elif len(metadata.tables) > 0:
            return None
        else:
            Table(FIELD_TABLE, metadata,
                  Column("field_name", String, primary_key=True),
                  Column("collection_name", String, primary_key=True),
                  Column(
                      "type", Enum(FIELD_TYPE_STRING, FIELD_TYPE_INTEGER, FIELD_TYPE_FLOAT, FIELD_TYPE_BOOLEAN,
                                   FIELD_TYPE_DATE, FIELD_TYPE_DATETIME, FIELD_TYPE_TIME,
                                   FIELD_TYPE_LIST_STRING, FIELD_TYPE_LIST_INTEGER,
                                   FIELD_TYPE_LIST_FLOAT, FIELD_TYPE_LIST_BOOLEAN, FIELD_TYPE_LIST_DATE,
                                   FIELD_TYPE_LIST_DATETIME, FIELD_TYPE_LIST_TIME, FIELD_TYPE_JSON, FIELD_TYPE_LIST_JSON),
                      nullable=False),
                  Column("description", String, nullable=True),
                  Column("visibility", Boolean, nullable=False),
                  Column("origin", Enum(TAG_ORIGIN_USER, TAG_ORIGIN_BUILTIN), nullable=False),
                  Column("unit", Enum(TAG_UNIT_MHZ, TAG_UNIT_DEGREE, TAG_UNIT_HZPIXEL, TAG_UNIT_MM, TAG_UNIT_MS), nullable=True),
                  Column("default_value", String, nullable=True))

            Table(COLLECTION_TABLE, metadata,
                  Column("collection_name", String, primary_key=True),
                  Column("primary_key", String, nullable=False))

            metadata.create_all(engine)
            return engine

    def __enter__(self):
        """
        Returns a DatabaseSession instance for using the database. This is
        supposed to be called using a "with" statement:

        with database as session:
           session.add_document(...)

        Therefore __exit__ must be called to get rid of the session.
        When called recursively, the underlying database session returned
        is the same. The commit/rollback of the session is done only by the
        outermost __enter__/__exit__ pair (i.e. by the outermost with
        statement).

        :return: the database session
        """
        # Create the session object
        new_session = self._Database__scoped_session()
        # Check if it is a brain new session object or if __enter__ already
        # added a DatabaseSession instance to it (meaning recursive call)
        db_session = getattr(new_session, '_populse_db_session', None)
        if db_session is None:
            # No recursive call. Create a new DatabaseSession
            # and attach it to the session. Doing this way allow
            # to be thread safe because scoped_session automatically
            # creates a new session per thread. Therefore we also
            # create a new DatabaseSession per thread.
            db_session = DatabaseSessionMIA(self, new_session)
            new_session._populse_db_session = db_session
            # Attache a counter to the session object to count
            # the recursion depth of __enter__ calls
            new_session._populse_db_counter = 1
        else:
            # __enter__ is called recursively. Simply increment
            # the recusive depth counter previously attached to
            # the session object
            new_session._populse_db_counter += 1
        return db_session

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Releases a DatabaseSession previously created by __enter__

        If no recursive call of __enter__ was done, the session
        is committed if no error is reported (e.g. exc_type is None)
        otherwise it is rolled back. Nothing is done
        """
        # Get the current session. SqlAlchemy scoped_session returns
        # the same object (per thread) on each call until remove()
        # is called.
        current_session = self._Database__scoped_session()
        # Decrement recursive depth counter
        current_session._populse_db_counter -= 1
        if current_session._populse_db_counter == 0:
            # If there is no recursive call, commit or rollback
            # the session according to the presence of an exception
            if exc_type is None:
                current_session.commit()
            else:
                current_session.rollback()
            # Delete the database session
            del current_session._populse_db_session
            del current_session._populse_db_counter
            self._Database__scoped_session.remove()


class DatabaseSessionMIA(DatabaseSession):
    """
    Class overriding the database session

    Methods:
        - add_collection: overrides the method adding a collection
        - add_fields: adds the list of fields
        - add_field: adds a field to the database, if it does not already exist
        - get_visibles: gives the list of visible tags
        - set_visibles: sets the list of visible tags
    """

    def add_collection(self, name, primary_key, visibility, origin, unit, default_value):
        """
        Overrides the method adding a collection

        :param name: New collection name
        :param primary_key: New collection primary_key column
        :param visibility: Primary key visibility
        :param origin: Primary key origin
        :param unit: Primary key unit
        :param default_value: Primary key default value
        """

        # Checks
        collection_row = self.get_collection(name)
        if collection_row is not None or name in self.table_classes:
            raise ValueError("A collection/table with the name " +
                             str(name) + " already exists")
        if not isinstance(name, str):
            raise ValueError("The collection name must be of type " + str(str) + ", but collection name of type " +
                             str(type(name)) + " given")
        if not isinstance(primary_key, str):
            raise ValueError("The collection primary_key must be of type " + str(str) +
                             ", but collection primary_key of type " + str(type(primary_key)) + " given")

        # Adding the collection row
        collection_row = self.table_classes[COLLECTION_TABLE](collection_name=name, primary_key=primary_key)
        self.session.add(collection_row)

        # Creating the collection document table
        pk_name = self.name_to_valid_column_name(primary_key)
        table_name = self.name_to_valid_column_name(name)
        collection_table = Table(table_name, self.metadata, Column(pk_name, String, primary_key=True))
        collection_query = CreateTable(collection_table)
        self.session.execute(collection_query)

        # Creating the class associated
        collection_dict = {'__tablename__': table_name, '__table__': collection_table}
        collection_class = type(table_name, (self.base,), collection_dict)
        mapper(collection_class, collection_table)
        self.table_classes[table_name] = collection_class

        # Adding the primary_key of the collection as field
        primary_key_field = self.table_classes[FIELD_TABLE](field_name=primary_key, collection_name=name,
                                             type=FIELD_TYPE_STRING, description="Primary_key of the document collection " + name, visibility=visibility, origin=origin, unit=unit, default_value=default_value)
        self.session.add(primary_key_field)

        if self._DatabaseSession__caches:
            self._DatabaseSession__documents[name] = {}
            self._DatabaseSession__fields[name] = {}
            self._DatabaseSession__fields[name][primary_key] = primary_key_field
            self._DatabaseSession__collections[name] = collection_row

        self.session.flush()

    def add_fields(self, fields):
        """
        Adds the list of fields

        :param fields: list of fields (collection, name, type, description, visibility, origin, unit, default_value)
        """

        collections = []

        for field in fields:
            # Adding each field
            self.add_field(field[0], field[1], field[2], field[3], field[4], field[5], field[6], field[7], False)
            if field[0] not in collections:
                collections.append(field[0])

        # Updating the table classes
        self.session.flush()

        # Classes reloaded in order to add the new column attribute
        self._DatabaseSession__update_table_classes()

        for collection in collections:
            self._DatabaseSession__refresh_cache_documents(collection)

    def add_field(self, collection, name, field_type, description, visibility, origin, unit, default_value,
                  index=False, flush=True):
        """
        Adds a field to the database, if it does not already exist

        :param collection: field collection (str)
        :param name: field name (str)
        :param field_type: field type (string, int, float, boolean, date, datetime,
                     time, list_string, list_int, list_float, list_boolean, list_date,
                     list_datetime, or list_time)
        :param description: field description (str or None)
        :param visibility: Bool to know if the field is visible in the databrowser
        :param origin: To know the origin of a field, in [TAG_ORIGIN_BUILTIN, TAG_ORIGIN_USER]
        :param unit: Origin of the field, in [TAG_UNIT_MS, TAG_UNIT_MM, TAG_UNIT_DEGREE, TAG_UNIT_HZPIXEL, TAG_UNIT_MHZ]
        :param default_value: Default_value of the field, can be str or None
        :param flush: bool to know if the table classes must be updated (put False if in the middle of filling fields) => True by default
        """

        # Checks
        collection_row = self.get_collection(collection)
        if collection_row is None:
            raise ValueError("The collection " +
                             str(collection) + " does not exist")
        field_row = self.get_field(collection, name)
        if field_row is not None:
            raise ValueError("A field with the name " +
                             str(name) + " already exists in the collection " + collection)
        if not isinstance(name, str):
            raise ValueError("The field name must be of type " + str(str) +
                             ", but field name of type " + str(type(name)) + " given")
        if field_type not in ALL_TYPES:
            raise ValueError("The field type must be in " + str(ALL_TYPES) + ", but " + str(
                field_type) + " given")
        if not isinstance(description, str) and description is not None:
            raise ValueError(
                "The field description must be of type " + str(
                    str) + " or None, but field description of type " + str(
                    type(description)) + " given")

        # Adding the field in the field table
        field_row = self.table_classes[FIELD_TABLE](field_name=name, collection_name=collection, type=field_type,
                                                    description=description, visibility=visibility, origin=origin,
                                                    unit=unit, default_value=default_value)

        if self._DatabaseSession__caches:
            self._DatabaseSession__fields[collection][name] = field_row

        self.session.add(field_row)

        # Fields creation
        if field_type in LIST_TYPES:
            if self.list_tables:
                table = 'list_%s_%s' % (self.name_to_valid_column_name(collection),
                                        self.name_to_valid_column_name(name))
                list_table = Table(table, self.metadata, Column('document_id', String, primary_key=True),
                                   Column('i', Integer, primary_key=True),
                                   Column('value', TYPE_TO_COLUMN[field_type[5:]]))
                list_query = CreateTable(list_table)
                self.session.execute(list_query)

                # Creating the class associated
                collection_dict = {'__tablename__': table, '__table__': list_table}
                collection_class = type(table, (self.base,), collection_dict)
                mapper(collection_class, list_table)
                self.table_classes[table] = collection_class

            # String columns if it list type, as the str representation of the lists will be stored
            field_type = String
        else:
            field_type = self._DatabaseSession__field_type_to_column_type(field_type)

        column = Column(self.name_to_valid_column_name(name), field_type, index=index)
        column_str_type = column.type.compile(self.database.engine.dialect)
        column_name = column.compile(dialect=self.database.engine.dialect)

        # Column created in document table, and in initial table if initial values are used

        document_query = str('ALTER TABLE "%s" ADD COLUMN %s %s' %
                             (self.name_to_valid_column_name(collection), column_name, column_str_type))
        self.session.execute(document_query)
        self.table_classes[self.name_to_valid_column_name(collection)].__table__.append_column(column)

        # Redefinition of the table classes
        if flush:
            self.session.flush()

            # Classes reloaded in order to add the new column attribute
            self._DatabaseSession__update_table_classes()

            if self._DatabaseSession__caches:
                self._DatabaseSession__refresh_cache_documents(collection)

        self.unsaved_modifications = True

    def get_visibles(self):
        """
        Gives the list of visible tags

        :return: the list of visible tags
        """

        visible_fields = self.session.query(
            self.table_classes[FIELD_TABLE]).filter(self.table_classes[FIELD_TABLE].visibility == True).all()
        visible_names = []
        for field in visible_fields:
            if field.field_name not in visible_names:
                visible_names.append(field.field_name)
        return visible_names

    def set_visibles(self, visibles):
        """
        Sets the list of visible tags

        :param visibles: list of visible tags
        """

        for field in self.session.query(self.table_classes[FIELD_TABLE]).all():
            if field.field_name in visibles:
                field.visibility = True
            else:
                field.visibility = False
            self.session.add(field)
        self.session.flush()
        self.unsaved_modifications = True
