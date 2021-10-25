import pygame
from pygame import mixer
import os
import random
import csv
import button

mixer.init()
pygame.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('War Game')


clock = pygame.time.Clock()
FPS = 60

#Variables del juego
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPE = 21
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False

#define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

#load music
pygame.mixer.music.load("music/ost1.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)


#Imagenes botones
start_img = pygame.image.load("img/menu/start_btn.png")
restart_img = pygame.image.load("img/menu/select_btn.png")
end_img = pygame.image.load("img/menu/end_btn.png")

#Fondo
mountain1_img = pygame.image.load("img/Background/mountain.png").convert_alpha()
sky_img = pygame.image.load("img/Background/sky_cloud.png").convert_alpha()

#Load imagenes
health_box_img = pygame.image.load("img/iconos/vida.png").convert_alpha()
#lista tile
img_list = []
for x in range (TILE_TYPE):
	img = pygame.image.load(f"img/tile/{x}.png")
	img = pygame.transform.scale(img,(TILE_SIZE,TILE_SIZE))
	img_list.append(img)
#Imagen bullet
bullet_img = pygame.image.load("img/iconos/bullet.png").convert_alpha()
#Imagen granada
grenade_img = pygame.image.load("img/iconos/grenade.png").convert_alpha()
#Cajas de item
health_box_img = pygame.image.load("img/iconos/vida.png").convert_alpha()
grenade_box_img = pygame.image.load("img/iconos/bomba.png").convert_alpha()
ammo_box_img = pygame.image.load("img/iconos/balas.png").convert_alpha()

#Contadores
ammo_cont_img = pygame.image.load("img/iconos/bomba_2.png").convert_alpha()
grenades_cont_img = pygame.image.load("img/iconos/bala_1.png").convert_alpha()

item_boxes = {
	"Health" : health_box_img ,
	"Ammo" : ammo_box_img ,
	"Grenade" : grenade_box_img
}
 

#Colores
BG = (144, 201, 120)
RED = (255 , 0, 0)
BLUE = (50 , 96,166)
VINO = (72 , 16,24)
GREEN = (7 , 255,44)
PURPLE = (233, 83,255)
BLACK = (0, 0,0)

def draw_bg():
	#Propiedades ventana
	width = sky_img.get_width()
	screen.fill(VINO)
	for x in range(5):
		screen.blit(sky_img,((x * width)-bg_scroll * 0.5,0))
		screen.blit(mountain1_img,(((x * width)-bg_scroll * 0.6),SCREEN_HEIGHT-mountain1_img.get_height()-40))

#Reiniciar valore
def reset_level():
	enemy_group.empty()
	bullet_group.empty()
	enemy_group.empty()
	explosion_group.empty()
	item_box_group.empty()
	decoration_group.empty()
	water_group.empty()
	exit_group.empty()

	#Crear tile list vacia
	data = []
	for row in range(ROWS):
		r = [-1] * COLS
		data.append(r)

	return data

#fuente
font = pygame.font.SysFont("Futura",30)
#Funcion texto en pantalla
def draw_text(text,font,text_col,x,y):
	img = font.render(text,True,text_col)
	screen.blit(img,(x,y))

class Soldier(pygame.sprite.Sprite):
	def __init__(self, char_type, x, y, scale, speed,ammo,grenades):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.char_type = char_type
		self.health = 100
		self.max_health = self.health
		self.speed = speed
		self.ammo = ammo
		self.star_ammo = ammo
		self.shoot_cooldown = 0
		self.grenades = grenades
		self.direction = 1
		self.vel_y = 0
		self.jump = False
		self.in_air= True
		self.flip = False
		self.animation_list = []
		self.update_time = pygame.time.get_ticks()
		self.frame_index = 0
		self.action = 0
		#ia variables
		self.move_counter = 0
		self.vision = pygame.Rect(0, 0, 150, 20)
		self.idling = False
		self.idling_counter = False

		#Listas de animaciones
		animation_types = ["stand","walk","jump","death"]
		for animation in animation_types:
			temp_list = []
			#Contar archivos en el folder
			num_frames = len(os.listdir(f"img/{self.char_type}/{animation}"))
			for i in range(num_frames):			
				img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
				img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
				temp_list.append(img)
			self.animation_list.append(temp_list)

		self.image = self.animation_list[self.action][self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()

	def update(self):
		self.update_animation()
		self.check_alive()
		#update cooldown
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1
						

	def move(self, moving_left, moving_right):
		#Reiniciar variables
		screen_scroll = 0
		dx = 0
		dy = 0

		#asignar movimiento derecha izquierda
		if moving_left:
			dx = -self.speed
			self.flip = True
			self.direction = -1
		if moving_right:
			dx = self.speed
			self.flip = False
			self.direction = 1		

		#Jump
		if self.jump == True and self.in_air == False:
			self.vel_y = -11
			self.jump = False
			self.in_air = True
		
		#Gravedad
		self.vel_y += GRAVITY
		if self.vel_y > 10:
			self.vel_y
		dy += self.vel_y

		#Chequear colisiones
		for tile in world.obstacle_list:
			#chequeo drireccion x
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				dx = 0
				#si la ia se encuentra con una pared
				if self.char_type == 'enemy':
					self.direction *= -1
					self.move_counter = 0
			#chequeo drireccion x
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				#chequeo salto
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				#Chequeo caida
				elif self.vel_y >= 0:
					self.vel_y = 0
					self.in_air=False
					dy = tile[1].top - self.rect.bottom
		#Chequeo
		if self.char_type == 'player':
			if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
				dx = 0
		#actualizar la posicion
		self.rect.x += dx
		self.rect.y += dy
		if pygame.sprite.spritecollide(self, water_group, False):
			self.health = 0

		level_complete = False
		if pygame.sprite.spritecollide(self, exit_group, False):
			level_complete = True

		if self.rect.bottom > SCREEN_HEIGHT:
			self.health = 0

		#Cargar scroll
		if self.char_type == 'player':
			if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
				or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
				self.rect.x -= dx
				screen_scroll = -dx
				
		return screen_scroll, level_complete

	def shoot(self):
		if self.shoot_cooldown == 0 and self.ammo > 0:
			self.shoot_cooldown = 20
			bullet = Bullet(self.rect.centerx + (0.95 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
			bullet_group.add(bullet)
			#reduce ammo
			self.ammo -= 1

	def ai(self):
		if self.alive and player.alive:
			if self.idling == False and random.randint(1,200) == 1:
				self.update_action(0)#0: stand
				self.idling = True
				self.idling_counter = 50
			#chequeo ai
			if self.vision.colliderect(player.rect):
				#Atacar jugador
				self.update_action(0)#0: stand
				self.shoot()	

			else:
				if self.idling == False:
					if self.direction == 1:
						ai_moving_right = True
					else:
						ai_moving_right = False

					ai_movig_left = not ai_moving_right			
					self.move (ai_movig_left,ai_moving_right)
					self.update_action(1)#1: run
					self.move_counter += 1
					#Cargar vision
					self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
					#Ver rango
					#pygame.draw.rect(screen,RED,self.vision)

					if self.move_counter > TILE_SIZE:
						self.direction *= -1
						self.move_counter *= -1
				
				else:
					self.idling_counter -= 1 
					if self.idling_counter <= 0:
						self.idling = False
		#Scroll
		self.rect.x += screen_scroll


	def update_animation(self):
		#Animacion
		ANIMATION_COOLDOWN = 100

		self.image = self.animation_list[self.action][self.frame_index]

		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1

		if self.frame_index >= len(self.animation_list[self.action]):
			#detener animacion
			if self.action == 3:
				self.frame_index =len(self.animation_list[self.action])-1
			else:
				self.frame_index = 0

	def update_action(self,new_action):
		#Revisar la accion
		if new_action != self.action:
			self.action = new_action
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()

	def check_alive(self):
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.alive = False
			self.update_action(3)


	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World():
	def __init__(self):
		self.obstacle_list = []

	def process_data(self, data):
		self.level_length = len(data[0])
		#iterate through each value in level data file
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >= 0:
					img = img_list[tile]
					img_rect = img.get_rect()
					img_rect.x = x * TILE_SIZE
					img_rect.y = y * TILE_SIZE
					tile_data = (img, img_rect)
					if tile >= 0 and tile <= 8:
						self.obstacle_list.append(tile_data)
					elif tile >= 9 and tile <= 10:
						water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
						water_group.add(water)
					elif tile >= 11 and tile <= 14:
						decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
						decoration_group.add(decoration)
					elif tile == 15:#create player
						player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
						health_bar = HealthBar(10, 10, player.health, player.health)
					elif tile == 16:#create enemies
						enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0)
						enemy_group.add(enemy)
					elif tile == 17:#create ammo box
						item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 18:#create grenade box
						item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 19:#create health box
						item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 20:#create exit
						exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
						exit_group.add(exit)

		return player, health_bar


	def draw(self):
		for tile in self.obstacle_list:
			tile[1][0] += screen_scroll
			screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
	
	def update(self):
		self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
	
	def update(self):
		self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
	
	def update(self):
		self.rect.x += screen_scroll

class ItemBox(pygame.sprite.Sprite):
	def __init__(self,item_type,x,y,):
		pygame.sprite.Sprite.__init__(self)

		self.item_type = item_type
		self.image = item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y +(TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll
		
		#colicion itembox
		if pygame.sprite.collide_rect(self,player):
			if self.item_type == "Health":
				player.health += 25				
				if player.health >= player.max_health:
					player.health = player.max_health


			elif self.item_type == "Ammo":
				player.ammo += 15

			elif self.item_type == "Grenade":
				player.grenades += 3

			#eliminar caja item
			self.kill()


class HealthBar():
	def __init__(self,x , y, health, max_health ):
		self.x = x 
		self.y = y
		self.health = health
		self.max_health = max_health

	def draw(self,health):
		#Cargar nueva vida
		self.health = health
		#Calcular ratio health
		ratio = self.health / self.max_health
		pygame.draw.rect(screen,BLACK,(self.x - 2,self.y - 2,154,24))
		pygame.draw.rect(screen,RED,(self.x,self.y,150,20))
		pygame.draw.rect(screen,GREEN,(self.x,self.y,150 * ratio,20))


class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 10
		self.image = bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction

	def update(self):
		#move bullet
		self.rect.x += (self.direction * self.speed) + screen_scroll
		#check if bullet has gone off screen
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill()
		#Chequeo de colisiones
		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect):
				self.kill()

		#check collision with characters
		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				player.health -= 5
				self.kill()

		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
				if enemy.alive:
					enemy.health -= 25
					self.kill()

class Grenade(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.timer = 100
		self.vel_y = -11
		self.speed = 7
		self.image = grenade_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.direction = direction

	def update(self):
		self.vel_y += GRAVITY
		dx = self.direction * self.speed
		dy = self.vel_y

		#check for collision with level
		for tile in world.obstacle_list:
			#check collision with walls
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				self.direction *= -1
				dx = self.direction * self.speed
			#check for collision in the y direction
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				self.speed = 0
				#check if below the ground, i.e. thrown up
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				#check if above the ground, i.e. falling
				elif self.vel_y >= 0:
					self.vel_y = 0
					dy = tile[1].top - self.rect.bottom


		
		#posicion granada
		self.rect.x += dx + screen_scroll
		self.rect.y += dy

		#Cuenta explosion
		self.timer -= 1
		if self.timer <= 0:
			self.kill()
			explosion = Explosion(self.rect.x,self.rect.y,0.5)
			explosion_group.add(explosion)
			#Daño de la granada
			if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
				abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
				player.health -= 50				
			for enemy in enemy_group:
				if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
				abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
					enemy.health -= 50

class Explosion(pygame.sprite.Sprite):

	def __init__(self,x,y,scale):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range (1,10):
			img = pygame.image.load(f"img/explosion/{num}.png").convert_alpha()
			img = pygame.transform.scale(img,(img.get_width()* scale,img.get_height()* scale))
			self.images.append(img)
			self.frame_index = 0
		self.image = self.images[self.frame_index]
		self.flip = False
		self.rect = self.image.get_rect()
		self.rect.center = ( x, y )
		self.counter = 0

	def update(self):
		self.rect.x += screen_scroll
		EXPLOSION_SPEED = 4

		#Cargar animacion explosion
		self.counter += 1
		if self.counter >= EXPLOSION_SPEED:
			self.counter = 0
			self.frame_index += 1
			#la animacion se completa
			if self.frame_index >= len(self.images):
				self.kill()
			else:
				self.image = self.images[self.frame_index]

class ScreenFade():
	def __init__(self, direction, colour, speed):
		self.direction = direction
		self.colour = colour
		self.speed = speed
		self.fade_counter = 0


	def fade(self):
		fade_complete = False
		self.fade_counter += self.speed
		if self.direction == 1:#whole screen fade
			pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
			pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT // 2 +self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
		if self.direction == 2:#vertical screen fade down
			pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
		if self.fade_counter >= SCREEN_WIDTH:
			fade_complete = True

		return fade_complete
 
# crear screen fade
intro_fade = ScreenFade(1,VINO, 4 )
death_fade = ScreenFade(2,BLACK, 4 )

#Crear botones
start_button = button.Button(SCREEN_HEIGHT // 2 - 130,SCREEN_HEIGHT // 2 - 150, start_img, 5 )
end_button = button.Button(SCREEN_HEIGHT // 2 - 120,SCREEN_HEIGHT // 2 + 50, end_img, 5 )
restart_button = button.Button(SCREEN_HEIGHT // 2 - 130,SCREEN_HEIGHT // 2 - 50, restart_img, 5 )

#Grupos de sprit
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

#Lista de tile
world_data = []
for row in range(ROWS):
	r = [-1] * COLS
	world_data.append(r)
#Cargar level y crear mundo
with open(f"level{level}_data.csv", newline="") as csvfile:
	reader = csv.reader(csvfile, delimiter = ",")
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)


#Bucle juego 
run = True
while run:

	clock.tick(FPS)
	if start_game == False:
		#Dibujar menu
		screen.fill(VINO)
		#add buttons
		if start_button.draw(screen):
			start_game = True
			start_intro = True

		if end_button.draw(screen):
			run = False


	else:
		#Fondo
		draw_bg()
		#Dibujar mapa
		world.draw()
		#Dibujar barra de vida
		health_bar.draw(player.health)
		#mostrar ammo
		draw_text("AMMO: " ,font, BLUE, 10, 35)
		for x in range (player.ammo):
			screen.blit(ammo_cont_img,(90+(x * 10),40))
		draw_text("GRENADE: " ,font, BLUE, 10, 60)
		for x in range (player.grenades):
			screen.blit(grenades_cont_img,(135+(x * 15),60))


		player.update()
		player.draw()

		for enemy in enemy_group:
			enemy.ai()
			enemy.update()
			enemy.draw()

		#cargar grupos
		bullet_group.update()
		grenade_group.update()
		explosion_group.update()
		item_box_group.update()
		decoration_group.update()
		water_group.update()
		exit_group.update()
		
		bullet_group.draw(screen)
		grenade_group.draw(screen)
		explosion_group.draw(screen)
		item_box_group.draw(screen)
		decoration_group.draw(screen)
		water_group.draw(screen)
		exit_group.draw(screen)

		#intro
		if start_intro == True:
			if intro_fade.fade():
				start_intro = False
				intro_fade.fade_counter = 0

		#Acciones jugador
		if player.alive:
			#shoot bullets
			if shoot:
				player.shoot()
			#throw grenades
			elif grenade and grenade_thrown == False and player.grenades > 0:
				grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
							player.rect.top, player.direction)
				grenade_group.add(grenade)
				#reduce grenades
				player.grenades -= 1
				grenade_thrown = True
			if player.in_air:
				player.update_action(2)#2: jump
			elif moving_left or moving_right:
				player.update_action(1)#1: run
			else:
				player.update_action(0)#0: idle
			screen_scroll, level_complete = player.move(moving_left, moving_right)
			bg_scroll -= screen_scroll
			#chequear si se completa el nivel
			if level_complete:
				start_level = True
				level += 1
				bg_scroll = 0
				world_data = reset_level()
				if level <= MAX_LEVELS:
					with open(f'level{level}_data.csv', newline='') as csvfile:
						reader = csv.reader(csvfile, delimiter=',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								world_data[x][y] = int(tile)
					world = World()
					player, health_bar = world.process_data(world_data)

		else:
			screen_scroll = 0
			if death_fade.fade():
				if restart_button.draw(screen):
					death_fade.fade_counter = 0
					start_intro = True
					bg_scroll = 0
					world_data = reset_level()
					with open(f'level{level}_data.csv', newline='') as csvfile:
						reader = csv.reader(csvfile, delimiter=',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								world_data[x][y] = int(tile)
					world = World()
					player, health_bar = world.process_data(world_data)


	for event in pygame.event.get():
		#quit game
		if event.type == pygame.QUIT:
			run = False
		#keyboard presses
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a:
				moving_left = True
			if event.key == pygame.K_d:
				moving_right = True
			if event.key == pygame.K_SPACE:
				print (player.health)
				shoot = True
			if event.key == pygame.K_q:
				grenade = True
			if event.key == pygame.K_w and player.alive:
				player.jump = True
			if event.key == pygame.K_ESCAPE:
				run = False


		#reiniciar controles
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False
			if event.key == pygame.K_SPACE:
				shoot = False
			if event.key == pygame.K_q:
				grenade = False
				grenade_thrown = False



	pygame.display.update()

pygame.quit()