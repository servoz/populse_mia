from enum import Enum


class OpStatus(Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"
    RUNNING = "running"
    
class FilterOperator(Enum):
    AND = "and"
    OR = "or"
    
class FilterOn(Enum):
    TAG = "Tag"
    FILENAME = "Filename"
    ATTRIBUTE = "Attribute"
    
class TagType(Enum):
    JSON = "Json"
    NIFTI = "Nifti"
    CUSTOM = "Custom"