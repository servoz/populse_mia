from enum import Enum


class OpStatus(Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"
    RUNNING = "running"
    UNEXECUTABLE = "unexecutable"
    
class FilterOperator(Enum):
    AND = "and"
    OR = "or"
    NONE = "none"
    
class FilterOn(Enum):
    TAG = "Tag"
    FILENAME = "Filename"
    ATTRIBUTE = "Attribute"
    BLANK = "Blank"
    
class TagType(Enum):
    JSON = "Json"
    NIFTI = "Nifti"
    CUSTOM = "Custom"