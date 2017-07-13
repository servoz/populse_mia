from uuid import uuid4

#It is the base of all other classes
#Every instanciated child will have a different generated unique uid
class GenericItem():
        
    def __init__(self):
        self.uid = str(uuid4())
        
    def getClassName(self):
        return self.__class__.__name__