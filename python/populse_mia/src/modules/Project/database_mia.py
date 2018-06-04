import populse_db
import hashlib
from sqlalchemy import create_engine, MetaData, String, Boolean, Integer, Enum, Column, Table
from sqlalchemy.schema import CreateTable
from sqlalchemy.orm import mapper

# Tag origin
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

class Database_mia(populse_db.database.Database):
    """
    Class overriding the default behavior of populse_db
    """

    def __init__(self, string_engine):

        super().__init__(string_engine, True, False)

    def create_empty_schema(self, string_engine):
        """
        Overrides the method creating the empty schema, in order to add columns to field table
        :param string_engine: Path of the new database file
        """

        engine = create_engine(string_engine)
        metadata = MetaData()

        Table(populse_db.database.FIELD_TABLE, metadata,
              Column("name", String, primary_key=True),
              Column("collection", String, primary_key=True),
              Column(
                  "type", Enum(populse_db.database.FIELD_TYPE_STRING, populse_db.database.FIELD_TYPE_INTEGER, populse_db.database.FIELD_TYPE_FLOAT, populse_db.database.FIELD_TYPE_BOOLEAN,
                               populse_db.database.FIELD_TYPE_DATE, populse_db.database.FIELD_TYPE_DATETIME, populse_db.database.FIELD_TYPE_TIME,
                               populse_db.database.FIELD_TYPE_LIST_STRING, populse_db.database.FIELD_TYPE_LIST_INTEGER,
                               populse_db.database.FIELD_TYPE_LIST_FLOAT, populse_db.database.FIELD_TYPE_LIST_BOOLEAN, populse_db.database.FIELD_TYPE_LIST_DATE,
                               populse_db.database.FIELD_TYPE_LIST_DATETIME, populse_db.database.FIELD_TYPE_LIST_TIME),
                  nullable=False),
              Column("description", String, nullable=True),
              Column("visibility", Boolean, nullable=False),
              Column("origin", Enum(TAG_ORIGIN_USER, TAG_ORIGIN_BUILTIN), nullable=False),
              Column("unit", Enum(TAG_UNIT_MHZ, TAG_UNIT_DEGREE, TAG_UNIT_HZPIXEL, TAG_UNIT_MM, TAG_UNIT_MS), nullable=True),
              Column("default_value", String, nullable=True))

        Table(populse_db.database.COLLECTION_TABLE, metadata,
              Column("name", String, primary_key=True),
              Column("primary_key", String, nullable=False))

        metadata.create_all(engine)

    def add_collection(self, name, primary_key, visibility, origin, unit, default_value):
        """
        Overrides the method adding a collection
        :param name: New collection name
        :param primary_key: New collection primary_key column
        :param visibility:
        :param origin:
        :param unit:
        :param default_value:
        """

        # Checks
        collection_row = self.get_collection(name)
        if collection_row is not None or name in self.table_classes:
            raise ValueError("A collection/table with the name " +
                             str(name) + " already exists")
        if not isinstance(name, str):
            raise ValueError("The collection name must be of type " + str(str) + ", but collection name of type " + str(type(name)) + " given")
        if not isinstance(primary_key, str):
            raise ValueError("The collection primary_key must be of type " + str(str) + ", but collection primary_key of type " + str(type(primary_key)) + " given")

        # Adding the collection row
        collection_row = self.table_classes[populse_db.database.COLLECTION_TABLE](name=name, primary_key=primary_key)
        self.session.add(collection_row)

        # Creating the collection document table
        collection_table = Table(name, self.metadata, Column(primary_key, String, primary_key=True))
        collection_query = CreateTable(collection_table)
        self.session.execute(collection_query)

        # Creating the class associated
        collection_dict = {'__tablename__': name, '__table__': collection_table}
        collection_class = type(name, (self.base,), collection_dict)
        mapper(collection_class, collection_table)
        self.table_classes[name] = collection_class

        # Adding the primary_key of the collection as field
        primary_key_field = self.table_classes[populse_db.database.FIELD_TABLE](name=primary_key, collection=name,
                                             type=populse_db.database.FIELD_TYPE_STRING, description="Primary_key of the document collection " + name, visibility=visibility, origin=origin, unit=unit, default_value=default_value)
        self.session.add(primary_key_field)

        if self._Database__caches:
            self._Database__documents[name] = {}
            self._Database__fields[name] = {}
            self._Database__fields[name][primary_key] = primary_key_field
            self._Database__names[name] = {}
            self._Database__names[name][primary_key] = primary_key
            self._Database__collections[name] = collection_row

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
        self._Database__update_table_classes()

        for collection in collections:
            self._Database__refresh_cache_documents(collection)

    def add_field(self, collection, name, field_type, description, visibility, origin, unit, default_value, flush=True):
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
        if not field_type in populse_db.database.ALL_TYPES:
            raise ValueError("The field type must be in " + str(populse_db.database.ALL_TYPES) + ", but " + str(
                field_type) + " given")
        if not isinstance(description, str) and description is not None:
            raise ValueError(
                "The field description must be of type " + str(
                    str) + " or None, but field description of type " + str(
                    type(description)) + " given")

        # Adding the field in the field table
        field_row = self.table_classes[populse_db.database.FIELD_TABLE](name=name, collection=collection, type=field_type,
                                                    description=description, visibility=visibility, origin=origin, unit=unit, default_value=default_value)

        if self._Database__caches:
            self._Database__fields[collection][name] = field_row
            self._Database__names[collection][name] = hashlib.md5(name.encode('utf-8')).hexdigest()

        self.session.add(field_row)

        # Fields creation
        if field_type in populse_db.database.LIST_TYPES:
            if self.list_tables:
                table = 'list_%s_%s' % (collection, self.field_name_to_column_name(collection, name))
                list_table = Table(table, self.metadata, Column('document_id', String, primary_key=True),
                                   Column('i', Integer, primary_key=True),
                                   Column('value', populse_db.database.TYPE_TO_COLUMN[field_type[5:]]))
                list_query = CreateTable(list_table)
                self.session.execute(list_query)

                # Creating the class associated
                collection_dict = {'__tablename__': table, '__table__': list_table}
                collection_class = type(table, (self.base,), collection_dict)
                mapper(collection_class, list_table)
                self.table_classes[table] = collection_class

                # sql = sql_text('CREATE TABLE %s (document_id VARCHAR, value %s)' % (table, str(self.field_type_to_column_type(field_type[5:])())))
                # self.session.execute(sql)
                # sql = sql_text('CREATE INDEX {0}_index ON {0} (document_id)'.format(table))
                # self.session.execute(sql)
            # String columns if it list type, as the str representation of the lists will be stored
            field_type = String
        else:
            field_type = self.field_type_to_column_type(field_type)

        column = Column(self.field_name_to_column_name(collection, name), field_type)
        column_str_type = column.type.compile(self._Database__engine.dialect)
        column_name = column.compile(dialect=self._Database__engine.dialect)

        # Column created in document table, and in initial table if initial values are used

        document_query = str('ALTER TABLE %s ADD COLUMN %s %s' %
                             (collection, column_name, column_str_type))
        self.session.execute(document_query)
        self.table_classes[collection].__table__.append_column(column)

        # Redefinition of the table classes
        if flush:
            self.session.flush()

            # Classes reloaded in order to add the new column attribute
            self._Database__update_table_classes()

            if self._Database__caches:
                self._Database__refresh_cache_documents(collection)

        self.unsaved_modifications = True