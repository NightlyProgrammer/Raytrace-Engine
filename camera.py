import pygame
import glm

class Camera:
    def __init__(self,start_position):
        self.pos = glm.vec3(*start_position)
        self.speed = 5
        self.rotation = glm.vec3(0,0,0)
        self.fov = 60

    def update(self,delta):
        #key input
        keys = pygame.key.get_pressed()

        speed = self.speed
        if keys[pygame.K_r]:
            speed *= 2
        if keys[pygame.K_w]:
            self.pos.x += glm.sin(self.rotation.y)*delta*speed
            self.pos.z += glm.cos(self.rotation.y)*delta*speed
        if keys[pygame.K_s]:
            self.pos.x -= glm.sin(self.rotation.y)*delta*speed
            self.pos.z -= glm.cos(self.rotation.y)*delta*speed
        if keys[pygame.K_a]:
            self.pos.x += glm.sin(self.rotation.y-glm.radians(90))*delta*speed
            self.pos.z += glm.cos(self.rotation.y-glm.radians(90))*delta*speed
        if keys[pygame.K_d]:
            self.pos.x += glm.sin(self.rotation.y+glm.radians(90))*delta*speed
            self.pos.z += glm.cos(self.rotation.y+glm.radians(90))*delta*speed

        if keys[pygame.K_SPACE]:
            self.pos.y += delta*speed
        if keys[pygame.K_LSHIFT]:
            self.pos.y -= delta*speed
        #mouse input(moving the camera)
        mouse_x_mov,mouse_y_mov = pygame.mouse.get_rel()
        self.rotation.y += glm.radians(mouse_x_mov)*delta*self.speed
        self.rotation.x += glm.radians(mouse_y_mov)*delta*self.speed
        #limit pitch (x rotation)
        self.rotation.x = min(max(self.rotation.x,glm.radians(-89)),glm.radians(89))