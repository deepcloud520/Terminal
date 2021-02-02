import pygame as pg
import tercore as tc
pg.init()
lo_font=pg.font.Font('Liberation Mono.ttf',14)
chi_font=pg.font.Font('simfang.ttf',14)
def printtext(text,font,x,y,color=(255,255,255),shadow=0):
    screen = pg.display.get_surface()
    if shadow:
        image=font.render(text,True,(0,0,0))
        screen.blit(image,(x+shadow,y+shadow))
    image=font.render(text,True,color)
    screen.blit(image,(x,y))
    pg.display.update()
class 