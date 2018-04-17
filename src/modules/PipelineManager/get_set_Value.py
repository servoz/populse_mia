from PipelineManager.Student import Student  # @UnresolvedImport


class get_set_Value(object):
        
    def setVar(self, *value):
        self._variab = value
        
    def main(self):
        self.res=Student(*self._variab)
        
    def getResult(self):
        return self.res