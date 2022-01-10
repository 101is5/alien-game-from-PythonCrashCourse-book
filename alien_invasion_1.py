# RESEARCH pygame AND sys MODULES
# NOT GONNA MAKE A SEPARATE FILE FOR THE SETTINGS FOR NOW
# REGARDLESS OF WHERE A FILE IS, IN VSCODE THE CURRENT FOLDER IS ALWAYS THE MAIN WORKSPACE FOLDER
# ANSWER THE EXERCISES AFTER COMPLETING THE GAME PROJECT

import sys
import pygame
import pygame.font
from pygame.sprite import Sprite
from pygame.sprite import Group
from time import sleep

class AlienInvasion:
    """Overall game class"""

    def __init__(self):
        """Initialize game/Create game resources"""
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((800,600))
        # self.screen = pygame.display.set_mode(
        #     (0, 0), pygame.FULLSCREEN)
        # self.settings.screen_width = self.screen.get_rect().width
        # self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")

        # Instances of stats, scoreboard, ship and groups of bullets and aliens
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # Play button
        self.play_button = Button(self,"PLAY")

    def run_game(self):
        """Starts main loop"""
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()

    def _check_events(self):
        # Listens to keyboard and mouse events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self,mouse_pos):
        """Start new game when clicking 'play' button"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # Reset game settings
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            pygame.mouse.set_visible(False)

            # Reset screen
            self.aliens.empty()
            self.bullets.empty()
            self._create_fleet()
            self.ship.center_ship()

    def _check_keydown_events(self,event):
        """Listens to keypresses"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self,event):
        """Listens to key releases"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _create_fleet(self):
        """Create all aliens"""
        # Make one alien/find number of aliens in a row
        # Spacing between each alien equals one alien's witdth
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2*alien_width)
        number_aliens_x = available_space_x // (2*alien_width) + 1
    
        # Determine number of aliens rows
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - 
                                (3*alien_height) - ship_height) 
        number_rows = available_space_y // (2*alien_height)

        # Create fleet of aliens
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self,alien_number,row_number):
        # Create an alien and place it in the row
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2*alien_width*alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2*alien.rect.height*row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached and edge"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop entire alien fleet"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _check_aliens_bottom(self):
        """Check if an alien hit the bottom of the screen"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Same logic as hitting the ship
                self._ship_hit()
                break

    def _fire_bullet(self):
        """Create bullet and adds it to bullet group"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """Update bullets positions"""
        self.bullets.update()
        # Clear shot bullets
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions"""
        # Check and remove colliding bullet/alien
        collisions = pygame.sprite.groupcollide(
                self.bullets,self.aliens,True,True)
            
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points*len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # Clear onscreen bullets and create new fleet
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            
            # Increase level
            self.stats.level += 1
            self.sb.prep_level()

    def _ship_hit(self):
        """Respond to ship being hit"""
        if self.stats.ships_left > 0:
            # Decrement ships_left
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # Remove remaining aliens and bullets
            self.aliens.empty()
            self.bullets.empty()

            # Create new flee and center the ship
            self._create_fleet()
            self.ship.center_ship()

            # Pause
            sleep(0.5)
        else: 
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _update_aliens(self):
        """Check if the fleet is at an edge,
        then update the positions of all aliens in the fleet
        """
        self._check_fleet_edges()
        self.aliens.update()

        # Look for alien-ship collisions
        if pygame.sprite.spritecollideany(self.ship,self.aliens):
            self._ship_hit()
        
        # Look for aliens hitting screen bottom
        self._check_aliens_bottom()

    def _update_screen(self):
        # Making a newly drawn screen
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        # Draw scoreboard
        self.sb.show_score()
        # Draw play button when game is inactive
        if not self.stats.game_active:
            self.play_button.draw_button()
        pygame.display.flip()

if __name__ == '__main__':
    # Make a game instance/Run the game
    ai = AlienInvasion()
    ai.run_game()


class Settings:
    """Stores the settings"""
   
    def __init__(self):
        """Initialize settings"""
        # Screen:
        self.screen_width = 800
        self.screen_height = 600
        self.bg_color = (230,230,230)

        # Ship:
        self.ship_limit = 3

        # Bullet:
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60,60,60)
        self.bullets_allowed = 3

        # Alien:
        self.fleet_drop_speed = 5

        # Speed up rate
        self.speedup_scale = 1.1

        # Point value increase rate
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        self.ship_speed = 1.5
        self.bullet_speed = 1.5
        self.alien_speed = 0.5

        # right = 1/left = -1
        self.fleet_direction = 1

        # Scoring
        self.alien_points = 50

    def increase_speed(self):
        """Also increase point values"""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale

        self.alien_points = int(self.alien_points*self.score_scale)
        # print(self.alien_points)


class Ship(Sprite):
    """Manages the ship"""
    
    def __init__(self,ai_game):
        """Initialize ship and set starting position"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()

        # Load ship image and get its rectangle
        self.image = pygame.image.load('images/ship.bmp')
        self.rect = self.image.get_rect()

        # Start each new ship at bottom center of screen
        self.rect.midbottom = self.screen_rect.midbottom

        # Store a decimal value for the ship's x position
        self.x = float(self.rect.x)

        # Movement flags
        self.moving_right = False
        self.moving_left = False
    
    def update(self):
        """Update ship's position"""
        # Update ship's x value, not rect
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed

        # Update rect object from self.x
        self.rect.x = self.x   

    def blitme(self):
        """Draw ship at current location"""
        self.screen.blit(self.image, self.rect)

    def center_ship(self):
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)

class Bullet(Sprite):
    """Manages the ship's bullets"""

    def __init__(self, ai_game):
        """Creates a bullet at the ship's position"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color

        # Create bullet at (0,0) then set correct position
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width,
            self.settings.bullet_height)
        self.rect.midtop = ai_game.ship.rect.midtop

        # Store bullet's position as float
        self.y = float(self.rect.y)
    
    def update(self):
        """Moves bullet"""
        # Update decimal position of bullet
        self.y -= self.settings.bullet_speed
        # Update rect position
        self.rect.y = self.y

    def draw_bullet(self):
        pygame.draw.rect(self.screen,self.color,self.rect)


class Alien(Sprite):
    """Represent one alien"""

    def __init__(self,ai_game):
        """Initialize alien/set starting position"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Load alien/set .rect
        self.image = pygame.image.load('images/alien.bmp')
        self.rect = self.image.get_rect()

        # Start each new alien top left
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Store alien's x position
        self.x = float(self.rect.x)

    def check_edges(self):
        """Return Trtue if alien hits edge"""
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right or self.rect.left <= 0:
            return True

    def update(self):
        """Move right"""
        self.x += (self.settings.alien_speed * 
                        self.settings.fleet_direction)
        self.rect.x = self.x


class GameStats:
    """Track statistics"""

    def __init__(self,ai_game):
        """Initialize statistics"""
        self.settings = ai_game.settings
        self.reset_stats()

        # Start game in active state
        self.game_active = False

        # High scores aren't reset
        self.high_score = 0

    def reset_stats(self):
        """Initialize in-game-changeable statistics"""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1


class Scoreboard:
    """Report score"""
    def __init__(self,ai_game):
        """Initialize score"""
        self.ai_game = ai_game
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings
        self.stats = ai_game.stats

        # Font settings
        self.text_color = (30,30,30)
        self.font = pygame.font.SysFont(None,48)

        # Prepare initial score image
        self.prep_score()
        self.prep_high_score()
        self.prep_level()
        self.prep_ships()
    
    def prep_score(self):
        """Turn score into rendered image"""
        rounded_score = round(self.stats.score, -1)
        score_str = "{:,}".format(rounded_score)
        # 'True' here activates antialiasing
        self.score_image = self.font.render(score_str,True,
                self.text_color,self.settings.bg_color)

        # Display score at the top right of the scren
        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - 20
        self.score_rect.top = 20

    def prep_high_score(self):
        """Turn highest score into rendered image"""
        high_score = round(self.stats.high_score, -1)
        high_score_str = "{:,}".format(high_score)
        self.high_score_image = self.font.render(high_score_str,True,
                self.text_color,self.settings.bg_color)

        # Center high score at top of screen
        self.high_score_rect = self.high_score_image.get_rect()
        self.high_score_rect.centerx = self.screen_rect.centerx
        self.high_score_rect.top = self.score_rect.top

    def show_score(self):
        """Draw score and level"""
        self.screen.blit(self.score_image,self.score_rect)
        self.screen.blit(self.high_score_image,self.high_score_rect)
        self.screen.blit(self.level_image,self.level_rect)
        self.ships.draw(self.screen)

    def check_high_score(self):
        """Check fro new high score"""
        if self.stats.score > self.stats.high_score:
            self.stats.high_score = self.stats.score
            self.prep_high_score()

    def prep_level(self):
        """Turn level number into rendered image"""
        level_str = str(self.stats.level)
        self.level_image = self.font.render(level_str,True,
                self.text_color, self.settings.bg_color)

        # Position level below score
        self.level_rect = self.level_image.get_rect()
        self.level_rect.right = self.score_rect.right
        self.level_rect.top = self.score_rect.bottom + 10

    def prep_ships(self):
        """Show how many ships are left"""
        self.ships = Group()
        for ship_number in range(self.stats.ships_left):
            ship = Ship(self.ai_game)
            ship.rect.x = 10 + ship_number*ship.rect.width
            ship.rect.y = 10
            self.ships.add(ship)


class Button:
     
    def __init__(self,ai_game,msg):
        """Initialize button attributes"""
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()

        # Set dimensions and propeties
        self.width, self.height = 200,50
        self.button_color = (0,255,0)
        self.text_color = (255,255,255)
        self.font = pygame.font.SysFont(None,48)

        # Build and center rect
        self.rect = pygame.Rect(0,0,self.width,self.height)
        self.rect.center = self.screen_rect.center

        # Button name
        self._prep_msg(msg)

    def _prep_msg(self,msg):
        """Converts text into rendered image/center text"""
        self.msg_image = self.font.render(msg,True,self.text_color,
                self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center
        
    def draw_button(self):
        # Draw button and message
        self.screen.fill(self.button_color,self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)