from engine import Engine
import pygame
from sys import exit

#note to self
#use a lot of space holder words in fragment shader and use pythons str.replace() method to replace them with the variables
def main():
    render_engine = Engine((1280,720),True)

    delta = 0
    menu_surf = pygame.image.load("minecraft_inventory_png_by_lildxxrling_deinzk7-fullview (1).png").convert_alpha()
    menu_surf = pygame.transform.scale_by(menu_surf,pygame.display.get_window_size()[1]/menu_surf.get_height())
    hub_open = False
    while True:
        render_engine.hud_surface.fill((0,0,0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                render_engine.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_1:
                        render_engine.take_screenshot("screenshots/")
                    case pygame.K_TAB:
                        hub_open = True
            elif event.type == pygame.KEYUP:
                match event.key:
                    case pygame.K_TAB:
                        hub_open = False

            elif event.type == pygame.MOUSEWHEEL:
                render_engine.camera.fov += event.y*delta*50
                render_engine.camera.fov = min(max(0,render_engine.camera.fov),180)
                #print(render_engine.camera.fov)

        if hub_open:
            render_engine.hud_surface.blit(menu_surf,(0,0))
        render_engine.update(delta)
        render_engine.render()

        pygame.display.flip()
        pygame.display.set_caption(str(round(render_engine.clock.get_fps())))
        delta = render_engine.clock.tick(60)*0.001
if __name__ == "__main__":
    main()