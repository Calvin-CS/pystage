import os
# from pystage.util import stderr_redirector
import sys
import io
import pygame
import pkg_resources
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import pystage

class CostumeManager():
    def __init__(self, owner):
        self.owner = owner
        self.costumes = []
        self.current_costume = -1

    def add_costume(self, name, center_x=None, center_y=None, factor=1):
        if isinstance(name, str):
            costume = Costume(self, name, center_x, center_y, factor)
            self.costumes.append(costume)
            if self.current_costume==-1:
                self.current_costume = len(self.costumes) - 1
                self.update_sprite_image()
        else:
            for n in name:
                self.add_costume(n)


    def replace_costume(self, index, name, center_x=None, center_y=None, factor=1):
        costume = Costume(self, name, center_x, center_y, factor)
        del self.costumes[index]
        self.costumes.insert(index, costume)
        self.update_sprite_image()


    def insert_costume(self, index, name, center_x=None, center_y=None, factor=1):
        costume = Costume(self, name, center_x, center_y, factor)
        self.costumes.insert(index, costume)
        self.update_sprite_image()

    def next_costume(self):
        if self.current_costume == -1:
            return
        self.current_costume += 1
        if self.current_costume == len(self.costumes):
            self.current_costume = 0
        self.update_sprite_image()

    def switch_costume(self, name):
        for i, costume in enumerate(self.costumes):
            if costume.name.lower().strip() == name.lower().strip():
                self.current_costume = i
                self.update_sprite_image()
                return

    def update_sprite_image(self):
        if isinstance(self.owner, pystage.core.CoreStage):
            return
        image, origin = self.rotate_and_scale()
        self.owner.image = image
        self.owner.rect = image.get_rect()
        self.owner.rect.topleft = origin

    def get_image(self):
        if self.current_costume == -1:
            return None
        return self.costumes[self.current_costume].image


    def get_costume(self):
        if self.current_costume == -1:
            return None
        return self.costumes[self.current_costume]

    
    def get_center(self):
        if self.current_costume == -1:
            return 0, 0
        return self.costumes[self.current_costume].center_x, self.costumes[self.current_costume].center_y


    def rotate_and_scale(self):
        # https://stackoverflow.com/questions/54462645/how-to-rotate-an-image-around-its-center-while-its-scale-is-getting-largerin-py
        pos = self.owner._pg_pos()
        originPos = self.get_center()
        # Rotation
        # Scratch is clockwise with 0 upwards
        # pyGame is counterclockwise with 0 to the right
        angle = 90-self.owner.direction
        zoom = self.owner.size/100
        image = self.get_image()

        # calcaulate the axis aligned bounding box of the rotated image
        w, h       = image.get_size()
        box        = [pygame.math.Vector2(p) for p in [(0, 0), (w, 0), (w, -h), (0, -h)]]
        box_rotate = [p.rotate(angle) for p in box]
        min_box    = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate, key=lambda p: p[1])[1])
        max_box    = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate, key=lambda p: p[1])[1])

        # calculate the translation of the pivot 
        pivot        = pygame.math.Vector2(originPos[0], -originPos[1])
        pivot_rotate = pivot.rotate(angle)
        pivot_move   = pivot_rotate - pivot

        # calculate the upper left origin of the rotated image
        move   = (-originPos[0] + min_box[0] - pivot_move[0], -originPos[1] - max_box[1] + pivot_move[1])
        origin = (pos[0] + zoom * move[0], pos[1] + zoom * move[1])

        # get a rotated image
        rotozoom_image = pygame.transform.rotozoom(image, angle, zoom)
      
        return rotozoom_image, origin

class Costume():
    '''
    This class handles and manages costumes and backdrops.
    '''
    def __init__(self, sprite, name, center_x=None, center_y=None, factor=1):
        self.sprite = sprite
        self.file = None
        self.name = name
        internal_folder = pkg_resources.resource_filename("pystage", "images/")
        for folder in ["", "images/", "bilder/", internal_folder]:
            for ext in ["", ".bmp", ".png", ".jpg", ".jpeg", ".gif", ".svg"]:
                if os.path.exists(f"{folder}{name}{ext}"):
                    self.file = f"{folder}{name}{ext}"
                    break
            if self.file is not None:
                break
        if self.file is None:
            self.file = pkg_resources.resource_filename("pystage", "images/zombie_idle.png")
        if self.file.endswith(".svg"):
            print(f"Converting SVG file: {self.file}")
            print("\nWARNING: SVG conversion is for convenience only")
            print("and might not work as expected. It is recommended")
            print("to manually convert to bitmap graphics (png or jpg).\n")
            # Deactivated for now because of Windows problems. See issue #10
            # with stderr_redirector(io.BytesIO()):
            rlg = svg2rlg(self.file)
            pil = renderPM.drawToPIL(rlg)
            self.image = pygame.image.frombuffer(pil.tobytes(), pil.size, pil.mode)
        else:
            self.image = pygame.image.load(self.file)
        if factor!=1:
            self.image = pygame.transform.rotozoom(self.image, 0, 1.0/factor)
            # self.image = pygame.transform.smoothscale(self.image, (int(self.image.get_width() / factor), int(self.image.get_height() / factor)))
        # self.image = self.image.subsurface(self.image.get_bounding_rect()) 
        self.center_x = self.image.get_width() / 2 if center_x is None else center_x / factor 
        self.center_y = self.image.get_height() / 2 if center_y is None else center_y / factor
        print(f"New costume: {name} -> {self.file}")


    def __str__(self):
        return f"{self.name} ({self.center_x}, {self.center_y})"


class SoundManager():
    def __init__(self, owner):
        self.owner = owner
        self.sounds = {}

    def add_sound(self, name):
        if isinstance(name, str):
            sound = Sound(self, name)
            self.sounds[name]=sound
        else:
            for n in name:
                self.add_sound(n)

    def get_sound(self, name):
        return self.sounds[name].sound


class Sound():
    '''
    This class handles and manages sounds.
    '''
    def __init__(self, sprite, name):
        self.name = name
        self.sprite = sprite
        self.file = None
        self.sound = None
        internal_folder = pkg_resources.resource_filename("pystage", "sounds/")
        for folder in ["", "sounds/", "klaenge/", internal_folder]:
            for ext in ["", ".wav", ".ogg", ".mp3"]:
                if os.path.exists(f"{folder}{name}{ext}"):
                    self.file = f"{folder}{name}{ext}"
                    break
            if self.file is not None:
                break
        if self.file.endswith(".mp3"):
            print("WARNING: MP3 is not supported in pyStage. Use wav or ogg format.")
        elif self.file is not None:
            self.sound = pygame.mixer.Sound(self.file)


    def __str__(self):
        return f"{self.name}"
