import pygame.mixer

from src.engine.config import *
from src.engine.utils import get_path, Timer


class SoundManager:
    sounds = {
        # 'bg': 'bg.wav'
        # 'boss1-intro': ['boss1', 'intro.wav'],
        # 'boss1-loop': ['boss1', 'loop.wav'],
        # 'bg': ['boss1', 'bg.ogg']
        'shoot': 'shoot.ogg',
        'contract_message': 'message.ogg',
        'notification': 'notification.ogg',
        'popup': 'popup.ogg',
        # 'music': 'music.ogg',
        'explosion': 'explosion1.ogg',
        'spark': 'explosion2.ogg',
        # 'click': 'click1.ogg',
        # 'hit': 'hit.ogg',
        # 'home_bg': 'game.ogg',
        # 'game_bg': 'game_bg_music.ogg',
        # 'shoot': 'shoot.wav',
        # 'slime': 'slime.wav'
    }
    # for i in range(1, 11):
    #     sounds[f'slime{i}'] = f'slime{i}.wav'

    sound_objects: dict[str, pygame.mixer.Sound] = {}
    bg_sound = 'bg.wav'
    home_page_sound = ''

    VOLUME = 100 * 0

    bg_music = pygame.mixer.music
    bg_channel: pygame.mixer.Channel = None

    timer = Timer('inf')

    @classmethod
    def set_bg_volume(cls, volume):
        if GAMESTATS.SPEAKERS_INIT:
            cls.bg_channel.set_volume(volume)

    @classmethod
    def update(cls):
        pass

    @classmethod
    def set_fadeout(cls, time):
        pass

    @classmethod
    def _get_volume(cls, percentage=100):
        return (percentage / 100) * cls.VOLUME / 100

    @classmethod
    def load_sounds(cls):
        for i, j in cls.sounds.items():
            print('loading... ', i, get_path('sounds', j))
            cls.sound_objects[i] = pygame.mixer.Sound(
                get_path('sounds', j).__str__())
        for i in cls.sound_objects:
            cls.sound_objects[i].set_volume(cls._get_volume())
        cls.bg_music.set_volume(cls._get_volume())
        pygame.mixer.set_reserved(1)
        cls.bg_channel = pygame.mixer.Channel(0)

    @classmethod
    def play(cls, sound, loops=0, preload=True, volume=100, end_event=None):
        if GAMESTATS.SPEAKERS_INIT:
            if preload:
                if sound in cls.sounds:
                    cls.sound_objects[sound].set_volume(volume / 100)
                    channel = cls.sound_objects[sound].play(loops)
                    # channel.set_endevent(end_event if end_event else EVENTS.SONG_FINISHED_EVENT)
            else:
                if sound in cls.sounds:
                    s = pygame.mixer.Sound(get_path('sounds', cls.sounds[sound]))
                    s.set_volume(volume / 100)
                    s.play(loops)

    @classmethod
    def stop(cls, sound, fadeout=100):
        if GAMESTATS.SPEAKERS_INIT:
            if sound in cls.sounds:
                cls.sound_objects[sound].fadeout(fadeout)

    @classmethod
    def play_bg(cls, sound, loops=-1, volume=100):
        sound = get_path('sounds', sound)
        if GAMESTATS.SPEAKERS_INIT:
            if sound in cls.sounds:
                cls.bg_channel.set_volume(volume / 100)
                cls.bg_channel.play(cls.sound_objects[sound], loops=loops)
                cls.bg_channel.set_endevent(EVENTS.SONG_FINISHED_EVENT)
            else:
                cls.bg_music.load(sound)
                cls.bg_music.play(loops)
                cls.bg_music.set_volume(volume / 100)
