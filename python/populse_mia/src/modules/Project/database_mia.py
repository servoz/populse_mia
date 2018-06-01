from populse_db.database import Database

class Database_mia(Database):
    """
    Class overriding the default behavior of populse_db
    """

    def __init__(self, string_engine):

        super().__init__(string_engine, True)