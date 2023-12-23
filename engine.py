import pygame
import numpy as np
import moderngl
from camera import Camera

from objects import Sphere,Object,Floor
from os import listdir

class Engine:
    def __init__(self,WINDOW_SIZE,fullscreen=False):
        pygame.init()
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION,3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION,3)
        if fullscreen:
            pygame.display.set_mode((0,0),pygame.OPENGL | pygame.DOUBLEBUF | pygame.FULLSCREEN)
        else:
            pygame.display.set_mode(WINDOW_SIZE,pygame.OPENGL | pygame.DOUBLEBUF)

        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        self.ctx = moderngl.create_context()
        self.clock = pygame.time.Clock()
        self.camera = Camera((0,0,-1))

        self.bg_img = self.load_texture("kloofendal_48d_partly_cloudy_puresky_4k (1).png")

        self.scene = [Sphere((0,0,0),(0,0,0),1,(1,1,1)),Sphere((13,2,0),(0,0,0),3,(1,0,0)),Floor(-5,(0.9333333333333333,0.9333333333333333,0.8235294117647058))]
        self.scene[1].reflectiveness = 0.4
        self.scene[-1].reflectiveness = 0.05

        self.vbo = self.ctx.buffer(np.array([
            (-1,1, 0,1),
            (-1,-1, 0,0),
            (1,1, 1,1),
            (1,-1, 1,0)
            ],dtype="f4"))

        with open("shader/vertex_shader.vert","r") as file: vertex_file_data = file.read()
        with open("shader/fragment_shader.frag","r") as file: fragment_file_data = file.read()

        #replace placeholder in fragment shader with the actual intersection function to the corresponding objs

        calculate_distance = "float dist=-1;\nfloat obj_dist,kr;\nint id;\nvec3 color,color2;\n"#calculates distance
        obj_intersect_functions = ""#defines all the intersect function before calling them
        obj_primitive_types = []#keeps track of primitives so you dont define the same intersect func twice 
        normal_function = "vec3 get_normal(vec3 hit_pos,int id){\n    switch(id){\n"
        normal_functions = ""
        for obj in self.scene:
            normal_function += f"        case {Object.list.index(obj)}:\n            return {obj.normal_fun_name+str(Object.list.index(obj))}(hit_pos);\n"
            normal_functions += obj.get_normal_function()+"\n"
            if type(obj) not in obj_primitive_types:
                obj_intersect_functions += obj.get_intersection_function()+"\n"
                obj_primitive_types.append(type(obj))
            calculate_distance += """
    obj_dist = obj.intersect_fun_name(ray_origin,dir,additional_parameters);
    if((obj_dist<dist && obj_dist>0) || dist<0){
        dist = obj_dist;
        id = obj.id;
        color = obj.color;
        color2 = obj.second_color;
        kr = obj.reflect;
    };
""".replace("obj.intersect_fun_name",obj.intersect_fun_name).replace(",additional_parameters",","+",".join([str(x) for x in obj.params])).replace("obj.id",str(Object.list.index(obj))).replace("obj.color",f"vec3{obj.color}").replace("obj.second_color",f"vec3{obj.second_color}").replace("obj.reflect",str(obj.reflectiveness))
        normal_function += "    }\n}\n"

        fragment_file_data = fragment_file_data.replace("#define_intersect_functions#",obj_intersect_functions)
        fragment_file_data = fragment_file_data.replace("#define_normal_functions",normal_functions)
        fragment_file_data = fragment_file_data.replace("#define_normal_function#",normal_function)
        fragment_file_data = fragment_file_data.replace("#calc_distance#",calculate_distance)

        print("\n".join([f"{i+1}. {line}" for i,line in enumerate(fragment_file_data.split("\n"))]))#basiclly a debugger feature to see all teh code in teh shader

        self.program = self.ctx.program(vertex_shader=vertex_file_data,fragment_shader=fragment_file_data)

        self.vao = self.ctx.vertex_array(self.program,[(self.vbo,"2f 2f","in_position","in_texcoord")])

        self.program["size"] = pygame.display.get_window_size()
        self.bg_img.use(0)
        self.program["background_image"] = 0

        #pygame related stuff
        self.hud_surface = pygame.Surface(pygame.display.get_window_size(),pygame.SRCALPHA)
        self.hud_texture = self.ctx.texture(self.hud_surface.get_size(),4)
        self.hud_texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.hud_texture.swizzle = 'BGRA'
        self.hud_texture.write(self.hud_surface.get_view('1'))
        self.hud_texture.use(1)
        self.program["hud_image"] = 1

        self.font = pygame.font.SysFont(None,int(24/1280*pygame.display.get_window_size()[0]))
    
    def update_hud(self):
        #write all the stuff that happens on the hud here
        #get virtual mouse pointer inside menu by having a mouse pointer coords set at (0,0) everytime the hud is opened and moving those coords through pygames get_rel function to not disturb the mouse bind to center of the screen

        self.hud_surface.blit(self.font.render(f"{round(self.clock.get_fps())} FPS - {self.camera.fov}° FOV",True,(255,255,255)),(0,0))

        self.hud_texture.write(self.hud_surface.get_view('1'))
        self.hud_texture.use(1)
        self.program["hud_image"] = 1

    def load_texture(self,path):
        surface = pygame.image.load(path).convert()
        new_texture = self.ctx.texture(surface.get_size(),4)
        new_texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        new_texture.swizzle = 'BGRA'
        new_texture.write(surface.get_view('1'))
        return new_texture

    def update(self,delta):
        self.camera.update(delta)
        self.update_hud()
        self.program["camera_pos"] = self.camera.pos
        self.program["camera_rotation"] = self.camera.rotation
        self.program["fov"] = np.radians(self.camera.fov)

    def render(self):
        self.vao.render(mode=moderngl.TRIANGLE_STRIP)
    
    def quit(self):
        self.vbo.release()
        self.program.release()
        self.vao.release()
        self.ctx.release()
        pygame.quit()
    
    def take_screenshot(self,path):
        n_of_screenshots = len([img for img in listdir(path) if img.split(".")[-1] == "png"])
        test = pygame.image.frombytes(self.ctx.screen.read(),pygame.display.get_window_size(),"RGB",True)
        pygame.image.save(test,path+f"screenshot{n_of_screenshots}.png")