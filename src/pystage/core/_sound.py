import pygame
from pygame.mixer import music
import time


class _Sound:

    # may deleted later

    # "sound_changeeffectby",   : change_sound_effect_by
    # "sound_changevolumeby",   : change_volume_by
    # "sound_cleareffects",     : clear_sound_effects
    # "sound_play",             : start_sound
    # "sound_playuntildone",    : play_sound_until_done
    # "sound_seteffectto",      : set_sound_effect_to
    # "sound_setvolumeto",      : change_volume_by
    # "sound_sounds_menu",      : ?
    # "sound_stopallsounds",    : stop_all_sounds
    # "sound_volume",           : get_volume

    #        {
    #          "opcode": "sound_changeeffectby",
    #          "params": {
    #            "EFFECT": "\"PITCH\"",
    #            "VALUE": 10.0
    #          },
    #          "next": false
    #        },
    #        {
    #          "opcode": "sound_changeeffectby",
    #          "params": {
    #            "EFFECT": "\"PAN\"",
    #            "VALUE": 10.0
    #          },
    #          "next": false
    #        },

    # Like for costumes and backdrops, we need a class structure here.
    # Plus a global sound manager.
    def __init__(self):
        self.mixer = pygame.mixer
        self.mixer.init()
        self.actual_pan = 0
        self.actual_pitch = 0

    def sound_play(self, sound, loop=0):
        channel = self.mixer.find_channel()
        channel.play(self.mixer.Sound(sound), loop)
        return channel

    def sound_playuntildone(self, sound):
        sound = self.mixer.Sound(sound)
        self.mixer.find_channel().play(sound, 0)
        time.sleep(sound.get_length())

    def sound_stopallsounds(self):
        self.mixer.stop()

    def sound_changeeffectby_pitch(self, value):
        # TODO: for pitching there is no ready to use code in pygame. To do so
        # we must operate on the audio array itself.

        # Similar to graphics effects
        # - pitch
        # - pan left/right
        # as volume is separate and we have only two effects,
        # it might be better to just create different methods.
        pass

    sound_changeeffectby_pitch.opcode = "sound_changeeffectby"
    sound_changeeffectby_pitch.param = "EFFECT"
    sound_changeeffectby_pitch.value = "PITCH"

    def sound_changeeffectby_pan(self, value):
        # norm pan value from -100/100 to range 0/1
        self.actual_pan = (value + 100) / 200
        self._apply_pan()

    sound_changeeffectby_pitch.opcode = "sound_changeeffectby"
    sound_changeeffectby_pitch.param = "EFFECT"
    sound_changeeffectby_pitch.value = "PAN"

    def sound_seteffectto(self, effect, value):
        pass

    def sound_cleareffects(self):
        self.actual_pan = 0
        self._apply_pan()

        self.actual_pitch = 0
        # apply pitch

    def _apply_pan(self):
        for channel_id in range(self.mixer.get_num_channels()):
            if self.actual_pan > 0:
                self.mixer.Channel(channel_id).set_volume(music.get_volume(), self.actual_pan)
            else:
                self.mixer.Channel(channel_id).set_volume(self.actual_pan, music.get_volume())

    def sound_changevolumeby(self, value, channel_id=None):
        value *= 0.01
        if channel_id is None:
            music.set_volume(self.sound_volume() + value)
        else:
            self.mixer.Channel(channel_id).set_volume(self.sound_volume(channel_id) + value)

    def sound_setvolumeto(self, value, channel_id=None):
        value *= 0.01
        if channel_id is None:
            music.set_volume(value)
        else:
            self.mixer.Channel(channel_id).set_volume(value)

    def sound_volume(self, channel_id=None):
        if channel_id is None:
            return music.get_volume() * 100
        else:
            return self.mixer.Channel(channel_id).get_volume() * 100

    def sound_sounds_menu(self):
        """
        Toggle sound menu.

        Returns
        -------
        None
        """
        pass
