#class for 3d objects that are rendered in the scene
from ray_intersection_functions import *
from primitive_normal_functions import *

class Object:
    list = []
    def __init__(self,pos,rot,color,intersect_fun,normal_fun,fun_names):
        self.position = pos
        self.rotation = rot
        self.color = color
        self.second_color = (0,0,0)
        self.reflectiveness = 0.6
        self.intersect_fun = intersect_fun
        self.intersect_fun_name = fun_names[0]
        self.normal_fun = normal_fun
        self.normal_fun_name = fun_names[1]
        self.params = [f"vec3{self.position}"]
        Object.list.append(self)

    def get_intersection_function(self,n_of_tabs=0):
        #add translation like rotation scale and positon
        #n_of_tabs is the number how tabs needed to be properly indented
        fun = "\n".join([f"{'    '*n_of_tabs+line}" for line in self.intersect_fun.split("\n")])
        return fun
    
    def get_normal_function(self,n_of_tabs=0):
        fun = "\n".join([f"{'    '*n_of_tabs+line}" for line in self.normal_fun.split("\n")])
        return fun.replace("object_position",f"vec3{self.position}").replace(self.normal_fun_name,self.normal_fun_name+str(Object.list.index(self)))
    
class Sphere(Object):
    def __init__(self,pos,rot,radius,color):
        super().__init__(pos,rot,color,SPHERE_INTERSECT,SPHERE_NORMAL,["raySphereIntersect","SphereNormal"])
        self.radius = radius
        self.params.append(self.radius)
    def get_intersection_function(self):
        fun = super().get_intersection_function()
        return fun
class Floor(Object):
    def __init__(self,height,color):
        super().__init__((0,height,0),(0,0,0),color,FLOOR_INTERSECT,FLOOR_NORMAL,["rayGroundIntersect","FloorNormal"])
        self.second_color = (0.4627450980392157,
0.5882352941176471,
0.33725490196078434)