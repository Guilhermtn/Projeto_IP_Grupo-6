import pygame
from enemy import *
from mapa import *
from random_drops import *

class game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode([1080, 720])
        self.fonte = pygame.font.SysFont('Arial', 55)


        #grupos de sprites usados
        self.enemy_group = pygame.sprite.Group()
        self.defense_group = pygame.sprite.Group()
        self.dropped_items_group = pygame.sprite.Group()
        self.projectile_group = pygame.sprite.Group()
        self.HUD_elements_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()

        self.all_sprites_group = pygame.sprite.Group()


        # gerador aleatório de drops no mapa 
        self.item_gen = drop_generator(self)

        # condicionais pro estado atual do jogo
        self.paused = False
        self.running = False
        self.in_menu = False
        self.in_pause_menu = False
        self.in_wave = False
        self.game_over = False
        self.win = False
        self.show_range = False
        

        # mapa 
        self.mapa = map()

        ##
        self.hp = 100
        self.money = 0
        self.current_wave = 0
        self.shield = False

        self.player = player(self)
        

    def update(self):
        
        if not self.paused:
            
            self.all_sprites_group.update()
            
            if self.in_wave:
                self.item_gen.update()

            # acabaram os inimigos na wave 
            if not self.enemy_group:
                    self.in_wave = False

            #player morreu
            if self.hp <= 0:
                self.game_over = True 
       
    def comandos(self):
        
        for command in pygame.event.get():
           
           #comandos globais(funcionam toda hora)

           #fecha o jogo
            if command.type == pygame.QUIT:
                self.running = False
          
           # pausa/despausa (ESC) 
            if command.type == pygame.KEYDOWN and command.key == pygame.K_ESCAPE:
                self.paused = not self.paused



            
            #comandos dentro do jogo(não funcionam se estiver em um menu/jogo pausado)
            if not self.paused and not self.in_menu:
                # spawna próxima wave de inimigos
                if command.type == pygame.KEYDOWN and command.key == pygame.K_SPACE and not self.in_wave:
                    self.start_wave(self.current_wave)
                    
                
                # limpa a tela de coletaveis
                if command.type == pygame.KEYDOWN and command.key == pygame.K_c:
                    
                    self.dropped_items_group = pygame.sprite.Group()

                
                if command.type == pygame.KEYDOWN and command.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    pos = self.player.pos       

                    #verifica se ja existe uma defesa na posição
                    can_place = all(not tower.rect.collidepoint(pos) for tower in self.defense_group)

                    #verifica se ta muito próximo do caminho dos inimigos
                    def point_near_path(point, path, threshold=50):  #threshold define a distancia minima permitida entre a defesa e o caminho dos inimigos

                        point = Vector2(point)
                        for i in range(len(path) - 1):
                            start = Vector2(path[i])
                            end = Vector2(path[i + 1])
                            closest = start + (end - start) * max(0, min(1, (point - start).dot(end - start) / (end - start).length_squared()))
                            if point.distance_to(closest) < threshold:
                                return True
                        return False

                    too_close_to_path = point_near_path(pos, self.mapa.waypoints)


                    if can_place and not too_close_to_path:
                        if command.key == pygame.K_1:
                            def_type1(self, pos)
                        elif command.key == pygame.K_2:
                            def_type2(self, pos)
                        elif command.key == pygame.K_3:
                            def_type3(self, pos)
                    
             
                if command.type == pygame.KEYDOWN and command.key == pygame.K_TAB:
                    self.show_range = not self.show_range
                    
    def start_wave(self, wave):
        self.in_wave = True
        
        if wave < len(self.mapa.waves):
            self.current_wave += 1
            new_enemies = self.mapa.waves[wave] # lista com os tipos de inimigos q precisa spawnar na wave 
            
            for enemy_type in new_enemies:
                if enemy_type == '':
                    pass
                if enemy_type == 1:
                    enem_type1(self)
                    
                elif enemy_type == 2:
                    enem_type2(self)
            
                elif enemy_type == 3:
                    enem_type3(self)

                
                # da tempo dps de spawnar um inimigo <------- n ta funcionando bom 
                for _ in range(5):
                    self.enemy_group.update() 
        

    def display(self, screen):
        # reset screen
        self.screen.fill((255, 255, 255))
        
        # tela game over
        if self.game_over:
            self.screen.blit(pygame.image.load('Assets/game_over.png').convert_alpha(),(0,0))
        # tela de vitoria
        elif self.win:
            self.screen.blit(pygame.image.load('Assets/game_over.png').convert_alpha(),(0,0)) # ainda ta usando a tela de game over
        else:



            # desenha o jogo quando n ta pausado
            if not self.paused:
                background = pygame.transform.scale(self.mapa.imagem, (1080, 720))
                screen.blit(background, (0, 0))
            
                # desenha os objetos do jogo
                self.enemy_group.draw(screen) 
                self.defense_group.draw(screen)
                self.dropped_items_group.draw(screen)
                self.projectile_group.draw(screen)
                self.HUD_elements_group.draw(screen)
                self.player_group.draw(screen)
                
                # range das defesas
                if self.show_range:
                    for tower in self.defense_group:
                        pygame.draw.circle(screen, 'black', tower.pos , tower.range - 15, 3)

                # HUD vida, talves mover isso pra uma classe de HUD (??)
                screen.blit(self.fonte.render(str(self.hp), True, (255, 255, 255)), (980, 0))
                screen.blit(pygame.image.load('Assets/heart.png').convert_alpha(), (920,7))
                if self.shield:
                     screen.blit(pygame.transform.scale(pygame.image.load('Assets/shield.png'), (60,60)), (855,0))

                #hud moeda
                screen.blit(self.fonte.render(str(self.money), True, (255, 255, 255)), (980, 50))
                screen.blit( pygame.transform.scale(pygame.image.load('Assets/coin.png'), (50,50)), (920,57))
                #numero de waves
                screen.blit(self.fonte.render(str(self.current_wave), True, (255, 255, 255)), (980, 120))
                screen.blit( pygame.transform.scale(pygame.image.load('Assets/enemy1.png'), (50,50)), (920,127))




                # HUD imagem de debug pra ver se tem uma wave ta acontecendo
                #if self.in_wave:
                   # screen.blit(pygame.image.load('Assets/enemy1.webp').convert_alpha(), (810, 7))

            
            


            # desenha tela de pause
            else:
                tela_pause = pygame.transform.scale(self.mapa.imagem, (1080, 720))
                screen.blit(tela_pause, (0, 0))
        
        
        pygame.display.flip()


    def run_game(self):
        self.screen = pygame.display.set_mode([1080, 720])
        self.running = True
        clock = pygame.time.Clock()

        while self.running:
            clock.tick(60)
            
            
            # inputs do usuário
            self.comandos()

            # update geral de todos os objetos do jogo
            self.update()

            # update do display
            self.display(self.screen)

    



        pygame.quit()




if __name__ == '__main__':
    jogo = game()
    jogo.run_game()
