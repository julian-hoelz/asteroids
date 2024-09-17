from pygame.mixer import Sound


FIRE: Sound # das Geräusch, das abgespielt wird, wenn der Spieler eine Kugel schießt
THRUST: Sound # das Geräusch des Schubs des Spielers
BANGSMALL: Sound # das Geräusch, das abgespielt wird, wenn ein kleiner Asteroid gesprengt wird
BANGMEDIUM: Sound
BANGLARGE: Sound
SAUCERSMALL: Sound
SAUCERBIG: Sound
BEAT1: Sound
BEAT2: Sound
MENU_SELECT: Sound
MENU_ACTION: Sound


def init():
    global FIRE, THRUST, BANGSMALL, BANGMEDIUM, BANGLARGE, SAUCERSMALL, SAUCERBIG, BEAT1, BEAT2, MENU_SELECT, MENU_ACTION
    FIRE = load_sound('fire.wav')
    THRUST = load_sound('thrust.wav')
    BANGSMALL = load_sound('bangsmall.wav')
    BANGMEDIUM = load_sound('bangmedium.wav')
    BANGLARGE = load_sound('banglarge.wav')
    SAUCERSMALL = load_sound('saucersmall.wav')
    SAUCERBIG = load_sound('saucerbig.wav')
    BEAT1 = load_sound('beat1.wav')
    BEAT2 = load_sound('beat2.wav')
    MENU_SELECT = load_sound('menu_select.mp3')
    MENU_ACTION = load_sound('menu_action.mp3')


def load_sound(filename):
    with open('sound/' + filename) as f:
        return Sound(f)