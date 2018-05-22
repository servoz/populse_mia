#!/usr/bin/python

class Student(object):
    def __init__(self,name,age,gender):
        self.name=name
        self.age=age
        self.gender=gender
        
    def affich(self):
        strq = 'your name is '+ self.name+', you have '+str(self.age) +' and you are '+self.gender
        return strq
    
    def agegroup(self):
        if int(self.age)<20:
            strs = 'young person'
        if int(self.age)>=20 and int(self.age)<=40:
            strs = 'adult person'
        if int(self.age)>40:
            strs = 'old person'
        return strs