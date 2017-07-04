from uuid import uuid4

class GenericItem():
        
    def __init__(self):
        self.uid = str(uuid4())
        
    def getClassName(self):
        return self.__class__.__name__