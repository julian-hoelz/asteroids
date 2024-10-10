from __future__ import annotations

# Fremde Imports

import json
import math
import pygame
import random
import time

from dataclasses import dataclass
from datetime import datetime
from typing import Callable

# Eigene Imports

import sounds


# Klassen

# Diese Klasse repräsentiert einen Vektor aus zwei Koordinaten:
class Vector:

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.tup = (x, y) # ein Tupel aus beiden Koordinaten

    
    # Diese Methode addiert einen Vektor zu diesem und gibt das Ergebnis als neuen Vektor zurück:
    def add(self, v: Vector) -> Vector:
        return Vector(self.x + v.x, self.y + v.y)
    

    # Diese Methode subtrahiert einen Vektor von diesem Vektor und gibt das Ergebnis als neuen Vektor zurück:
    def sub(self, v: Vector) -> Vector:
        return Vector(self.x - v.x, self.y - v.y)


    # Diese Methode multipliziert diesen Vektor mit einem Faktor und gibt das Ergebnis als neuen Vektor zurück:
    def mult(self, f: float) -> Vector:
        return Vector(self.x * f, self.y * f)


    # Diese Methode setzt die Magnitüde dieses Vektors und gibt das Ergebnis als neuen Vektor zurück:
    def set_mag(self, mag: float) -> Vector:
        prev_mag = self.mag()
        x = self.x * mag / prev_mag # Diese Rechnung skaliert den Vektor so, dass seine Magnitüde den übergebenen Wert beträgt
        y = self.y * mag / prev_mag
        return Vector(x, y)


    # Diese Methode reduziert die Magnitüde auf einen Maximalwert, wenn sie diesen überschreitet, und gibt das Ergebnis als neuen
    # Vektor zurück:
    def limit(self, max_mag: float) -> Vector:
        mag = self.mag()
        if mag > max_mag: # Wenn die maximale Magnitüde überschritten wird
            return self.set_mag(max_mag)
        else:
            return Vector(self.x, self.y)
    

    # Diese Methode gibt die Magnitüde dieses Vektors zurück:
    def mag(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2) # Satz des Pythagoras
    
    
    # Diese Methode gibt die Entfernung dieses Vektors zu einem anderen zurück:
    def distance(self, other: Vector) -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
    

    # Diese Methode gibt ein Dictionary mit den Werten dieses Vektors zurück:
    def to_dict(self) -> dict[str, float]:
        return {
            'x': self.x,
            'y': self.y
        }


# Diese Klasse repräsentiert eine Polarkoordinate aus einem Winkel (Theta) und einem Radius:
class PolarCoordinate:

    def __init__(self, theta: float, radius: float) -> None:
        self.theta = theta
        self.radius = radius

    
    # Diese Methode gibt den dieser Polarkoordinate entsprechenden kartesischen Vektor zurück:
    def cartesian(self) -> Vector:
        x = self.radius * math.cos(self.theta)
        y = self.radius * math.sin(self.theta)
        return Vector(x, y)
    

    # Diese Methode gibt ein Dictionary mit den Werten dieser Polarkoordinate zurück:
    def to_dict(self) -> dict[str, float]:
        return {
            'theta': self.theta,
            'radius': self.radius
        }


# Diese Klasse repräsentiert ein Polygon mit eine Mitte und Polarkoordinaten:
class Polygon:
    
    def __init__(self, center: Vector, polar_coordinates: tuple[PolarCoordinate], stroke_weight: int, visible: bool) -> None:
        self.center = center # die Mitte des Polygons
        self.polar_coordinates = polar_coordinates # die Polarkoordinaten des Polygons
        self.stroke_weight = stroke_weight # die Dicke der Umrandung
        self.visible = visible # ob das Polygon sichtbar ist


    # Diese Methode gibt ein Tupel aus den kartesischen Koordinaten dieses Polygons zurück:
    def cartesian(self) -> tuple[Vector]:
        # jede Koordinate in eine kartesische Koordinate umrechnen, in einem Tupel speichern und zurückgeben:
        return tuple(c.cartesian().add(self.center) for c in self.polar_coordinates)


    # Diese Methode gibt zurück, ob ein Vektor in diesem Polygon liegt:
    def vector_in(self, vector: Vector) -> bool:
        cartesian = self.cartesian()
        if len(cartesian) < 3:
            return False
        count = 0
        for i in range(len(cartesian)):
            v1 = cartesian[i]
            v2 = cartesian[(i + 1) % len(cartesian)]
            if ((v1.y > vector.y) != (v2.y > vector.y)) and (vector.x < (v2.x - v1.x) * (vector.y - v1.y) / (v2.y - v1.y) + v1.x):
                count += 1
        return count % 2 == 1


    # Diese Methode gibt zurück, ob dieses Polygon mit einem anderen Polygon kollidiert:
    def collides_with_polygon(self, polygon: Polygon) -> bool:
        # prüfen, ob ein Vektor des anderen Polygons in diesem Polygon liegt:
        for v in polygon.cartesian():
            if self.vector_in(v):
                return True
        # prüfen, ob ein Vektor dieses Polygons im anderen Polygon liegt:
        for v in self.cartesian():
            if polygon.vector_in(v):
                return True
        return False # Wenn keine Kollision erkannt wurde, „falsch“ zurückgeben
    

    # Diese Methode rotiert dieses Polygon:
    def rotate(self, angle: float) -> None:
        for c in self.polar_coordinates: # den Winkel zu den Winkeln aller Polarkoordinaten addieren
            c.theta += angle

    
    # Diese Methode bewegt dieses Polygon:
    def move(self, vector: Vector) -> None:
        self.center = self.center.add(vector) # den Vektor zur Mitte dieses Polygons addieren

    
    # Diese Methode rendert dieses Polygon:
    def render(self, screen: pygame.Surface) -> None:
        if self.visible: # wenn dieses Polygon sichtbar ist
            vectors = self.cartesian()
            for i in range(len(vectors)):
                pygame.draw.line(screen, Color.WHITE, vectors[i].tup, vectors[(i + 1) % len(vectors)].tup, self.stroke_weight)


    # Diese Methode gibt ein Dictionary mit den Werten dieses Polygons zurück:
    def to_dict(self) -> dict[str, object]:
        return {
            'center': self.center.to_dict(),
            'polar_coordinates': [c.to_dict() for c in self.polar_coordinates],
            'stroke_weight': self.stroke_weight,
            'visible': self.visible
        }


# TODO kommentieren

# Diese Klasse repräsentiert das Raumschiff des Spielers:
class Player:

    def __init__(self, body: Polygon | None, thrust: Polygon | None, turning_angle: float, mot: Vector | None, ticks: int) -> None:
        # der Körper des Spielers:
        self.body = body
        if body is None:
            self.body = Polygon(center=CENTER, polar_coordinates=(
                PolarCoordinate(-math.pi / 2, 20),
                PolarCoordinate(2 * math.pi * 0.14, 20),
                PolarCoordinate(2 * math.pi * 0.16, 12),
                PolarCoordinate(2 * math.pi * 0.34, 12),
                PolarCoordinate(2 * math.pi * 0.36, 20)
            ), stroke_weight=2, visible=True)
        # der Schub:
        self.thrust = thrust
        if thrust is None:
            self.thrust = Polygon(center=CENTER, polar_coordinates=(
                PolarCoordinate(2 * math.pi * 0.2, 15),
                PolarCoordinate(2 * math.pi * 0.25, 22),
                PolarCoordinate(2 * math.pi * 0.3, 15)
            ), stroke_weight=2, visible=False)
        # der Rest:
        self.turning_angle = turning_angle
        self.mot = Vector(0.0, 0.0) if mot is None else mot
        self.ticks = ticks # wie viele Ticks der Spieler schon lebt


    # Diese Methode dreht den Spieler leicht nach links:
    def turn_left(self) -> None:
        # 0,01 vom Drehungswinkel abziehen und das Minimum setzen
        self.turning_angle = max(self.turning_angle - 0.01, -MAX_TURNING_SPEED)

    
    # Diese Methode dreht den Spieler leicht nach rechts:
    def turn_right(self) -> None:
        # 0,01 zum Drehungswinkel addieren und das Maximum setzen
        self.turning_angle = min(self.turning_angle + 0.01, MAX_TURNING_SPEED)


    # Diese Methode aktualisiert die Bewegung dieses Spielers:
    def foreward(self) -> None:
        acc = PolarCoordinate(self.body.polar_coordinates[0].theta, 0.5).cartesian() # das, was zur Bewegung hinzukommt
        self.mot = self.mot.add(acc)
        self.mot = self.mot.limit(MAX_SPEED) # die Bewegung begrenzen


    # Diese Methode kümmert sich um die Ränder. Wenn der Spieler an den Seiten das Fenster verlässt, wird er auf die andere Seite
    # teleportiert:
    def edges(self) -> None:
        if self.body.center.x < -30:
            new_x = self.body.center.x + WIDTH + 60
            self.body.center.x = new_x
            self.thrust.center.x = new_x
        elif self.body.center.x > WIDTH + 30:
            new_x = self.body.center.x - WIDTH - 60
            self.body.center.x = new_x
            self.thrust.center.x = new_x
        if self.body.center.y < -30:
            new_y = self.body.center.y + HEIGHT + 60
            self.body.center.y = new_y
            self.thrust.center.y = new_y
        elif self.body.center.y > HEIGHT + 30:
            new_y = self.body.center.y - HEIGHT - 60
            self.body.center.y = new_y
            self.thrust.center.y = new_y


    # Diese Methode wird einmal pro Tick aufgerufen und aktualisiert die Position und die Drehung des Spielers:
    def update(self) -> None:
        self.turning_angle *= TURNING_FRICTION # die Drehung mit Reibung abbremsen
        self.mot = self.mot.limit(self.mot.mag() * FRICTION) # die Bewegung abbremsen

        # wenn der Spieler die Taste W oder die Pfeiltaste nach oben drückt:
        if pygame.key.get_pressed()[pygame.K_w] or pygame.key.get_pressed()[pygame.K_UP]:
            self.foreward() # Vorwärts!
            self.thrust.visible = True # den Schub sichtbar machen
        else:
            self.thrust.visible = False # den Schub unsichtbar machen
        
        # wenn die Taste A oder die Pfeiltaste nach links gedrückt sind:
        if pygame.key.get_pressed()[pygame.K_a] or pygame.key.get_pressed()[pygame.K_LEFT]:
            # wenn weder die Taste D noch die Pfeiltaste nach rechts gedrückt ist:
            if not (pygame.key.get_pressed()[pygame.K_d] or pygame.key.get_pressed()[pygame.K_RIGHT]):
                self.turn_left()
        # wenn weder die Taste A noch die Pfeiltaste nach links gedrückt ist, dafür aber die Taste D oder die
        # Pfeiltaste nach rechts:
        elif pygame.key.get_pressed()[pygame.K_d] or pygame.key.get_pressed()[pygame.K_RIGHT]:
            self.turn_right()

        # den Körper und den Schub des Raumschiffs drehen:
        self.body.rotate(self.turning_angle)
        self.thrust.rotate(self.turning_angle)

        # den Körper und den Schub des Raumschiffs bewegen:
        self.body.center = self.body.center.add(self.mot)
        self.thrust.center = self.thrust.center.add(self.mot)

        self.edges() # siehe Kommentar über der Funktion edges()
        self.ticks += 1


    # Diese Methode rendert diesen Spieler:
    def render(self, screen: pygame.Surface) -> None:
        # Wenn der Spieler erst kürzer als die Unbesiegbarkeitszeit existiert, wird er blinkend angezeigt:
        if self.ticks >= INVINCIBILITY_TIME or self.ticks % (FPS // 3) in range(FPS // 6):
            self.body.render(screen)
            if self.ticks % (FPS // 10) in range(FPS // 20): # auch der Schub wird (schneller) blinkend angezeigt
                self.thrust.render(screen)

    
    # Diese Funktion gibt ein Dictionary mit den Werten dieses Spielers zurück:
    def to_dict(self) -> dict[str, object]:
        return {
            'body': self.body.to_dict(),
            'thrust': self.thrust.to_dict(), 
            'turning_angle': self.turning_angle,
            'motion': self.mot.to_dict(),
            'ticks': self.ticks
        }


# Dies ist eine Klasse für Größen von Asteroiden:
@dataclass
class AsteroidSize:

    avg_radius: float # der durchschnittliche Radius (die durchschnittliche Entfernung der Koordinaten von der Mitte)
    min_speed: float
    max_speed: float # die Geschwindigkeit soll ein Wert zwischen min_speed und max_speed werden
    stroke_weight: int # die Dicke der Umrandung
    points: int # die Anzahl von Punkten, die man für das Zerstören erhält
    index: int # der Index dieser Asteroidgröße


# Diese Klasse repräsentiert einen Asteroiden:
class Asteroid:

    def __init__(self, size: AsteroidSize, body: Polygon, mot_angle: float, mot: Vector, rot: float, hit_by: int) -> None:
        self.size = size
        self.body = body
        self.mot_angle = mot_angle
        self.mot = mot
        self.rot = rot
        self.hit_by = hit_by


    # Diese Methode wird einmal pro Tick aufgerufen und aktualisiert die Position und die Drehung dieses Asteroiden:
    def update(self) -> None:
        self.body.move(self.mot)
        self.body.rotate(self.rot)

    
    # Diese Methode prüft, ob dieser Asteroid von einer Kugel getroffen wird:
    def check_hit(self, bullets: list[Bullet], by: int) -> None:
        for b in bullets:
            if self.body.vector_in(b.pos): # wenn dieser Asteroid von der Kugel getroffen wird
                self.hit_by = by 
                bullets.remove(b) # die Kugel aus der Liste entfernen
                break # Es ist nicht weiter nötig zu prüfen, ob dieser Asteroid getroffen wird


    # Diese Methode rendert diesen Asteroiden:
    def render(self, screen: pygame.Surface) -> None:
        self.body.render(screen)

    
    # Diese Methode prüft, ob dieser Asteroid aus dem Fenster verschwunden ist:
    def offscreen(self) -> bool:
        return self.body.center.distance(CENTER) > ASTEROID_DESPAWN_DISTANCE
    

    # Diese Methode gibt ein Dictionary aus den Werten dieses Asteroiden zurück:
    def to_dict(self) -> dict[str, object]:
        return {
            'size': self.size.index,
            'body': self.body.to_dict(),
            'motion_angle': self.mot_angle,
            'motion': self.mot.to_dict(),
            'rotation': self.rot,
            'hit_by': self.hit_by
        }


# Eine Klasse für Größen von fliegenden Untertassen:
@dataclass
class SaucerSize:
    
    def __init__(self, radius: float, stroke_weight: int, min_speed: float, max_speed: float, points: int, aim: float,
                 shoot_probability: float, bullet_lifetime: int, sound: int, index: int) -> None:
        self.radius = radius
        self.stroke_weight = stroke_weight # die Dicke der Umrandung
        self.min_speed = min_speed
        self.max_speed = max_speed # Es wird ein zufälliger Wert zwischen min_speed und max_speed als Geschwindigkeit gesetzt
        self.points = points # die Anzahl von Punkten, die man bekommt, wenn man die fliegende Untertasse zerstört
        self.aim = aim # die Zielgenauigkeit
        self.shoot_probability = shoot_probability / FPS # die Wahrscheinlichkeit, dass die fliegende Untertasse eine Kugel abschießt
        self.bullet_lifetime = int(bullet_lifetime * FPS) # die Lebenszeit einer Kugel der fliegenden Untertasse
        self.sound = sound # das Geräusch, das immer wieder abgespielt wird, wenn eine fliegende Untertasse der Größe im Fenster ist
        self.index = index


# Diese Klasse repräsentiert eine fliegende Untertasse
class Saucer:

    def __init__(self, size: SaucerSize, body: Polygon, mot: Vector, speed: float, steps: int, ticks: int, hit_by: int) -> None:
        self.size = size
        self.body = body
        self.mot = mot
        self.speed = speed
        self.steps = steps
        self.ticks = ticks
        self.hit_by = hit_by


    # Diese Methode gibt zurück, ob diese fliegende Untertasse noch im Fenster ist:
    def on_screen(self) -> bool:
        if self.body.center.x < -self.size.radius:
            return False
        if self.body.center.x > WIDTH + self.size.radius:
            return False
        if self.body.center.y < -self.size.radius:
            return False
        if self.body.center.y > HEIGHT + self.size.radius:
            return False
        return True

    
    # Diese Methode wird bei jedem Tick aufgerufen und aktualisiert diese fliegende Untertasse:
    def update(self) -> None:
        self.body.move(self.mot)
        if self.ticks == self.steps: # Wenn die fliegende Untertasse an ihrem Ziel angekommen ist, neues Ziel anvisieren
            self.ticks = -1
            self.steps = random.randint(SAUCER_MIN_STEPS, SAUCER_MAX_STEPS)
            self.mot = PolarCoordinate(random.random() * 2 * math.pi, self.speed).cartesian()
        self.ticks += 1

    
    # Diese Methode prüft, ob diese fliegende Untertasse von einer Kugel getroffen worden ist:
    def check_hit(self, bullets: list[Bullet], by: int) -> None:
        for b in bullets:
            if self.body.vector_in(b.pos):
                self.hit_by = by
                bullets.remove(b)
                break
    

    # Diese Methode rendert diese fliegende Untertasse:
    def render(self, screen: pygame.Surface) -> None:
        self.body.render(screen) # die Umrandung anzeigen
        
        # die zwei Linien, die von links nach rechts gezeichnet werden:
        l1a = self.body.polar_coordinates[1].cartesian().add(self.body.center).tup
        l1b = self.body.polar_coordinates[6].cartesian().add(self.body.center).tup
        l2a = self.body.polar_coordinates[2].cartesian().add(self.body.center).tup
        l2b = self.body.polar_coordinates[5].cartesian().add(self.body.center).tup
        
        # die zwei Linien zeichnen:
        pygame.draw.line(screen, Color.WHITE, l1a, l1b, self.size.stroke_weight)
        pygame.draw.line(screen, Color.WHITE, l2a, l2b, self.size.stroke_weight)

    
    # Diese Methode gibt ein Dictionary mit den Werten dieser fliegenden Untertasse zurück:
    def to_dict(self) -> dict[str, object]:
        return {
            'size': self.size.index,
            'body': self.body.to_dict(),
            'motion': self.mot.to_dict(),
            'speed': self.speed,
            'steps': self.steps,
            'ticks': self.ticks,
            'hit_by': self.hit_by
        }


# Diese Klasse repräsentiert eine Kugel, die vom Spieler abgeschossen wurde. Die Klasse SaucerBullet, die eine Kugel repräsentiert,
# die von einer fliegenden Untertasse abgeschossen wurde, erbt von dieser Klasse:
class Bullet:

    def __init__(self, pos: Vector, mot: Vector) -> None:
        self.pos = pos # Position
        self.mot = mot # Bewegung (motion)

    
    # Diese Methode wird einmal pro Tick aufgerufen und aktualisiert diese Kugel:
    def update(self) -> None:
        self.pos = self.pos.add(self.mot) # die Bewegung zur Position addieren

    
    # Diese Methode rendert diese Kugel:
    def render(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, Color.WHITE, self.pos.tup, BULLET_RADIUS) # die Kugel auf das Fenster zeichnen
         

    # Diese Methode gibt zurück, ob diese Kugel zu entfernen ist:
    def to_remove(self) -> bool:
        if self.pos.x < -30: # über den linken Fensterrand hinaus
            return True
        if self.pos.x > WIDTH + 30: # über den rechten Fensterrand hinaus
            return True
        if self.pos.y < -30: # über den oberen Bildschirmrand hinaus
            return True
        if self.pos.y > HEIGHT + 30: # über den unteren Bildschirmrand hinaus
            return True
        return False # noch auf dem Fenster oder nicht zu weit vom Fensterrand entfernt
    

    # Diese Methode gibt ein Dictionary mit den Werten dieser Kugel zurück:
    def to_dict(self) -> dict[str, object]:
        return {
            'position': self.pos.to_dict(),
            'motion': self.mot.to_dict()
        }


# Diese Klasse repräsentiert eine Kugel, die von einer fliegenden Untertasse abgeschossen wurde:
class SaucerBullet(Bullet):

    def __init__(self, pos: Vector, mot: Vector, lifetime: int, ticks: int) -> None:
        super().__init__(pos, mot)
        self.lifetime = lifetime # wie viele Ticks die Kugel existiert
        self.ticks = ticks

    
    # Diese Methode wird einmal pro Tick aufgerufen und aktualisiert diese von einer fligenden Untertasse abgeschossene Kugel:
    def update(self) -> None:
        super().update()
        self.ticks += 1


    # Diese Methode gibt zurück, ob diese von einer fliegenden Untertasse abgeschossene Kugel zu entfernen ist:
    def to_remove(self) -> bool:
        # Rückgabe: ob entweder die Ticks höher sind als die Lebenszeit der Kugel oder to_remove() in der Superklasse wahr ist:
        return self.ticks >= self.lifetime or super().to_remove()
    

    # Diese Methode gibt ein Dictionary mit den Werten dieser von einer fligenden Untertasse abgeschossenen Kugel zurück:
    def to_dict(self) -> dict[str, object]:
        return {
            'position': self.pos.to_dict(),
            'motion': self.mot.to_dict(),
            'lifetime': self.lifetime,
            'ticks': self.ticks
        }


# Diese Klasse repräsentiert ein Fragment. Ein Fragment entsteht, wenn ein Spieler oder eine fliegende Untertasse zerstört wird:
class Fragment:

    def __init__(self, lines: list[Line], ticks: int) -> str:
        self.lines = lines
        self.ticks = ticks

    
    # Diese Methode wird einmal pro Tick aufgerufen und aktualisiert dieses Fragment:
    def update(self) -> None:
        for l in self.lines:
            l.update() # alle Linien aktualisieren
        self.ticks += 1


    # Diese Methode rendert dieses Fragment:
    def render(self, screen: pygame.Surface) -> None:
        for l in self.lines: # alle Linien rendern
            l.render(screen)

    
    # Diese Methode gibt ein Dictionary mit den Werten dieses Fragments zurück:
    def to_dict(self) -> dict[str, object]:
        return {
            'lines': [l.to_dict() for l in self.lines],
            'ticks': self.ticks
        }


# Diese Klasse repräsentiert eine Linie mit einem Mittelpunkt, zwei Polarkoordinaten, einer Bewegung und einer Rotation:
class Line:

    def __init__(self, center: Vector, center_to_a: PolarCoordinate, center_to_b: PolarCoordinate, mot: Vector, rot: float,
                 stroke_weight: int) -> None:
        self.center = center # der Mittelpunkt
        self.center_to_a = center_to_a # eine Polarkoordinate: vom Mittelpunkt zum Punkt A
        self.center_to_b = center_to_b # eine Polarkoordinate: vom Mittelpunkt zum Punkt B
        self.mot = mot # Bewegung (motion)
        self.rot = rot # Rotation
        self.stroke_weight = stroke_weight # die Dicke der Linie
    

    # Diese Methode aktualisiert diese Linie:
    def update(self) -> None:
        # die Rotation zu den Theta-Winkeln der beiden Polarkoordinaten addieren:
        self.center_to_a.theta += self.rot
        self.center_to_b.theta += self.rot

        self.center = self.center.add(self.mot) # bewegen
        
        self.rot *= FRICTION # die Rotation abbremsen
        self.mot = self.mot.mult(FRICTION) # die Bewegung abbremsen

    
    # Diese Methode rendert diese Linie:
    def render(self, screen: pygame.Surface) -> None:
        a = self.center_to_a.cartesian().add(self.center).tup # der Punkt A als Tupel
        b = self.center_to_b.cartesian().add(self.center).tup # der Punkt B als Tupel
        pygame.draw.line(screen, Color.WHITE, a, b, self.stroke_weight)


    # Diese Methode gibt ein Dictionary mit den Werten dieser Linie zurück:
    def to_dict(self) -> dict[str, object]:
        return {
            'center': self.center.to_dict(),
            'center_to_a': self.center_to_a.to_dict(),
            'center_to_b': self.center_to_b.to_dict(),
            'motion': self.mot.to_dict(),
            'rotation': self.rot,
            'stroke_weight': self.stroke_weight
        }


# Diese Klasse repräsentiert eine Explosion aus mehreren Partikeln, die beim Sprengen eines kleinen Asteroiden entsteht:
class Explosion:

    def __init__(self, particles: list[Particle]) -> None:
        self.particles = particles

    
    # Diese Methode aktualisiert diese Explosion:
    def update(self) -> None:
        for p in self.particles:
            p.update() # alle Partikel aktualisieren
    

    # Diese Methode rendert diese Explosion:
    def render(self, screen: pygame.Surface) -> None:
        for p in self.particles:
            p.render(screen) # alle Partikel rendern

    
    # Diese Methode gibt zurück, ob diese Explosion zu entfernen ist:
    def to_remove(self) -> bool:
        return False not in (p.to_remove() for p in self.particles) # wahr, wenn alle Partikel zu entfernen sind
    

    # Diese Methode gibt ein Dictionary mit den Werten dieser Explosion zurück:
    def to_dict(self) -> dict[str, object]:
        return {
            'particles': [p.to_dict() for p in self.particles]
        }


# Diese Klasse repräsentiert ein Partikel, aus dem Explosionen bestehen
class Particle:

    def __init__(self, pos: Vector, mot: Vector, ticks: int, lifetime: int) -> None:
        self.pos = pos
        self.mot = mot
        self.ticks = ticks
        self.lifetime = lifetime

    
    # Diese Funktion wird einmal pro Tick aufgerufen und aktualisiert dieses Partikel:
    def update(self) -> None:
        self.pos = self.pos.add(self.mot) # bewegen
        self.ticks += 1

    
    # Diese Funktion rendert dieses Partikel:
    def render(self, screen: pygame.Surface) -> None:
        if self.ticks < self.lifetime: # wenn dieses Partikel noch angezeigt werden soll
            pygame.draw.circle(screen, Color.WHITE, self.pos.tup, 2) # dieses Partikel als kleinen Kreis auf das Fenster zeichnen

    
    # Diese Methode gibt zurück, ob dieses Partikel zu entfernen ist:
    def to_remove(self) -> bool:
        return self.ticks >= self.lifetime
    

    # Diese Methode gibt ein Dictionary mit den Werten dieses Partikels zurück:
    def to_dict(self) -> dict[str, object]:
        return {
            'position': self.pos.to_dict(),
            'motion': self.mot.to_dict(),
            'ticks': self.ticks,
            'lifetime': self.lifetime
        }


# Diese Klasse repräsentiert ein Menü, durch das der Spieler navigieren kann:
class Menu:

    def __init__(self, title: str, text: str | None, transparent: bool, parent: Menu | None, button_data: tuple[ButtonData, ...]) -> None:
        self.title_surface = TITLE_FONT.render(title, True, Color.WHITE) # die Textoberfläche für den Titel rendern
        self.title_pos = ((WIDTH - self.title_surface.get_width()) / 2, 100) # die Position des Titels
        self.set_text(text)
        self.transparent = transparent
        self.parent = parent
        
        # den Hintergrund (der transparent ist oder nicht) erstellen
        self.background = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(self.background, Color.BLACK_ALPHA if transparent else Color.BLACK, self.background.get_rect())
        
        # Die Buttons konstruieren:
        start_y = 225 if text is None else self.text_positions[-1].y + self.text_surfaces[-1].get_height() + 50
        self.buttons = tuple([Button(d.text, start_y + i * 50, d.active, d.on_action) for (i, d) in enumerate(button_data)])
        
        self.select_top_button()


    def set_text(self, text: str | None, update_buttons_y: bool = False) -> None:
        if text is None:
            self.text_surfaces = ()
            self.text_positions = ()
        else:
            # die Textoberflächen der Buttons:
            self.text_surfaces = tuple(TEXT_FONT.render(line, True, Color.WHITE) for line in text.split('\n'))
            # die Positionen der Buttons:
            self.text_positions = tuple(Vector((WIDTH - s.get_width()) / 2, 205 + i * s.get_height())
                                        for (i, s) in enumerate(self.text_surfaces))

        if update_buttons_y:
            # die y-Koordinaten aller Buttons aktualisieren:
            for (i, b) in enumerate(self.buttons):
                b.y = self.text_positions[-1].y + self.text_surfaces[-1].get_height() + 50 + i * 50


    # Diese Funktion wählt alle Buttons dieses Menüs ab:
    def deselect_all_buttons(self) -> None:
        for b in self.buttons:
            b.selected = False # alle Buttons abwählen


    # Diese Funktion wählt den obersten aktiven Button dieses Menüs aus:
    def select_top_button(self) -> None:
        self.deselect_all_buttons() # alle Buttons abwählen
        for b in self.buttons:
            if b.active: # den obersten aktiven Button finden
                b.selected = True
                return


    # Diese Funktion wird aufgerufen, wenn der Spieler in diesem Menü die Entertaste drückt:
    def action(self) -> None:
        for b in self.buttons:
            if b.selected: # den ausgewählten Button finden
                b.on_action()
                sounds.MENU_ACTION.play()
                return


    # Diese Funktion wird aufgerufen, wenn der Spieler in diesem Menü die Taste W oder die Pfeiltaste nach oben drückt.
    # Sie wählt den Button über dem zuvor ausgewählten Button aus:
    def select_button_above(self) -> None:
        for (i, b) in enumerate(self.buttons):
            if b.selected: # den ausgewählten Button finden
                # der Button über dem ausgewählten Button oder None, wenn keiner darüber ist:
                button_above = self.__get_button_above(i)
                
                if button_above is not None:
                    b.selected = False
                    button_above.selected = True
                    sounds.MENU_SELECT.play()
                    return

    
    # Diese Funktion wird aufgerufen, wenn der Spieler in diesem Menü die Taste S oder die Pfeiltaste nach unten drückt.
    # Sie wählt den Button unter dem zuvor ausgewählten Button aus:
    def select_button_below(self) -> None:
        for (i, b) in enumerate(self.buttons):
            if b.selected: # den ausgewählten Button finden
                # der Button unter dem ausgewählten Button oder None, wenn keiner darunter ist:
                button_below = self.__get_button_below(i)

                if button_below is not None:
                    b.selected = False
                    button_below.selected = True
                    sounds.MENU_SELECT.play()
                    return

    
    # Diese Funktion findet den Button über dem gerade ausgewählten Button:
    def __get_button_above(self, index: int) -> Button | None:
        if index == 0:
            return None # Wenn der oberste Button ausgewählt ist, gibt es keinen Button darüber
        for i in range(index - 1, -1, -1):
            if self.buttons[i].active: # den ersten Button über dem gerade ausgewählten finden
                return self.buttons[i] # diesen zurückgeben
        return None # wenn kein Button gefunden wurde
    

    # Diese Funktion findet den Button unter dem gerade ausgewählten Button:
    def __get_button_below(self, index: int) -> Button | None:
        if index == len(self.buttons) - 1:
            return None # Wenn der unterste Button ausgewählt ist, gibt es keinen Button darunter
        for i in range(index + 1, len(self.buttons)):
            if self.buttons[i].active: # den ersten Button unter dem gerade ausgewählten finden
                return self.buttons[i] # diesen zurückgeben
        return None # wenn kein Button gefunden wurde


    # Diese Funktion rendert dieses Menü:
    def render(self, screen: pygame.Surface) -> None:
        screen.blit(self.background, (0, 0)) # den Hintergrund malen
        screen.blit(self.title_surface, self.title_pos) # den Titel platzieren
        for (s, p) in zip(self.text_surfaces, self.text_positions):
            screen.blit(s, p.tup) # alle Texte an ihren Positionen platzieren
        for b in self.buttons:
            b.render(screen) # alle Buttons rendern


# Diese Klasse repräsentiert einen Button in einem Menü, den man mit den Pfeiltasten auswählen kann:
class Button:

    def __init__(self, text: str, y: int, active: bool, on_action: Callable) -> None:
        self.text_surface = BUTTON_FONT.render(text, True, Color.WHITE) # die weiße Textoberfläche für diesen Button rendern
        self.gray_text_surface = BUTTON_FONT.render(text, True, Color.GRAY) # die graue Textoberfläche für diesen Button rendern
        self.x = (WIDTH - self.text_surface.get_width()) / 2 # die x-Koordinate berechnen, sodass der Button mittig angezeigt wird
        self.y = y # die y-Koordinate des Buttons zuweisen
        self.active = active
        self.on_action = on_action
        self.selected = False # anfangs ist der Button nicht ausgewählt

    
    def render(self, screen: pygame.Surface) -> None:
        # Die Textoberfläche (weiß wenn ausgewählt, sonst grau) anzeigen:
        surface = self.text_surface if self.active else self.gray_text_surface
        screen.blit(surface, (self.x, self.y))
        
        # Wenn der Button ausgewählt ist, links und rechts zwei Pfeile anzeigen:
        if self.selected:
            # die Punkte der zwei Polygone berechnen, die die Pfeile beschreiben:
            p1v1 = (self.x - 10, self.y + self.text_surface.get_height() / 2) # Polygon 1 Vektor 1
            p1v2 = (self.x - 25, self.y + self.text_surface.get_height() * 0.25) # Polygon 1 Vektor 2
            p1v3 = (self.x - 25, self.y + self.text_surface.get_height() * 0.75) # Polygon 1 Vektor 3
            p2v1 = (self.x + self.text_surface.get_width() + 10, p1v1[1]) # Polygon 2 Vektor 1
            p2v2 = (self.x + self.text_surface.get_width() + 25, p1v2[1]) # Polygon 2 Vektor 2
            p2v3 = (self.x + self.text_surface.get_width() + 25, p1v3[1]) # Polygon 2 Vektor 3
            
            # die Polygone auf das Fenster zeichnen:
            pygame.draw.line(screen, Color.WHITE, p1v1, p1v2)
            pygame.draw.line(screen, Color.WHITE, p1v1, p1v3)
            pygame.draw.line(screen, Color.WHITE, p2v1, p2v2)
            pygame.draw.line(screen, Color.WHITE, p2v1, p2v3)
            
            # pygame.draw.polygon(screen, Color.WHITE, (p1v1, p1v2, p1v3))
            # pygame.draw.polygon(screen, Color.WHITE, (p2v1, p2v2, p2v3))


# Diese Datenklasse repräsentiert einen Highscore:
@dataclass
class HighScore:

    score: int # die Punktzahl
    timestamp: int # der Zeitstempel, wann der Highscore erreicht wurde

    # Diese Methode gibt ein Dictionary mit den Werten des Highscores zurück:
    def to_dict(self) -> dict[str, int]:
        return {
            'score': self.score,
            'timestamp': self.timestamp
        }


# Diese Klasse enthält einige Farben:
class Color:
    BLACK = (0, 0, 0) # Schwarz
    WHITE = (255, 255, 255) # Weiß
    GRAY = (80, 80, 80) # Grau
    RED = (255, 0, 0) # Rot
    GREEN = (0, 255, 0) # Grün
    ORANGE = (255, 127, 0) # Orange
    BLACK_ALPHA = (0, 0, 0, 127) # Schwarz mit 50 % Deckkraft


# Dies ist eine Klasse für Schwierigkeitsstufen
class Difficulty:
    
    def __init__(self, asteroid_spawn_chance: float, start_at_seconds: int) -> None:
        # Die Wahrscheinlichkeit, dass ein Asteroid spawnt, wird durch die FPS geteilt, um sie daran anzupassen:
        self.asteroid_spawn_chance = asteroid_spawn_chance / FPS
        
        # Die Sekunden, wann die Schwierigkeit starten soll, werden mit den FPS multipliziert, um sie in Ticks umzurechnen:
        self.starts_at_ticks = start_at_seconds * FPS


# Dies ist eine Datenklasse für die Daten eines Buttons:
@dataclass
class ButtonData:

    text: str # der Text des Buttons
    active: bool # ob der Button aktiv ist
    on_action: Callable # was beim Drücken der Entertaste geschehen soll, wenn dieser Button ausgewählt ist


# Konstanten

WIDTH = 800 # die Breite des Fensters
HEIGHT = 600 # die Höhe des Fensters
SIZE = (WIDTH, HEIGHT)
CENTER = Vector(WIDTH / 2, HEIGHT / 2) # die Mitte des Fensters als Vektor
PERIMETER = WIDTH * 2 + HEIGHT * 2 # der Umfang des Fensters
# wie wahrscheinlich es sein soll, dass etwas an einer bestimmten Seite spawnt:
SIDE_PROBABILITIES = [WIDTH / PERIMETER, HEIGHT / PERIMETER, WIDTH / PERIMETER, HEIGHT / PERIMETER]

FPS = 60 # die Bildfrequenz
INVINCIBILITY_TIME = 3 * FPS # die Anzahl von Ticks, wie lange der Spieler nach einer Kollision unbesiegbar sein soll (3 Sekunden)

MAX_TURNING_SPEED = 0.1 # die maximale Drehgeschwindigkeit des Spielers
TURNING_FRICTION = 0.925 # die Reibung, die das Drehen des Spielers abbremst
MAX_SPEED = 7.5 # die maximale Geschwindigkeit des Spielers
FRICTION = 0.975 # die Reibung, die die Bewegung des Spielers abbremst

SAUCER_MIN_STEPS = FPS * 3 # wie lange eine fliegende Untertasse sich mindestens in eine Richtung bewegt
SAUCER_MAX_STEPS = FPS * 5 # wie lange eine fliegende Untertasse sich höchstens in eine Richtung bewegt

BULLET_SPEED = 10 # die Geschwindigkeit, mit der Kugeln sich bewegen
BULLET_RADIUS = 2 # der Radius von Kugeln

ASTEROID_SPAWN_DISTANCE: int # die Entfernung zur Fenstermitte, mit der Asteroiden spawnen (wird in init_constants() gesetzt)
ASTEROID_DESPAWN_DISTANCE: int # die Entfernung zur Fenstermitte, mit der Asteroiden despawnen (wird in init_constants() gesetzt)

SCORE_FONT: pygame.font.Font # die Schriftart, mit der der Punktestand angezeigt wird
HIGHSCORE_FONT: pygame.font.Font # die Schriftart, mit der der Highscore angezeigt wird
TITLE_FONT: pygame.font.Font # die Schriftart, mit der Titel angezeigt werden
TEXT_FONT: pygame.font.Font # die Schriftart, mit der Texte in Menüs angezeigt werden
BUTTON_FONT: pygame.font.Font # die Schriftart, mit der Texte in Buttons angezeigt werden

# die Größen, mit denen Asteroiden spawnen können, und dazugehörige Werte (s. AsteroidSize für die Bedeutungen der Attribute):
ASTEROID_SIZES = {
    'small': AsteroidSize(avg_radius=15, min_speed=2.4, max_speed=3.6, stroke_weight=1, points=100, index=0),
    'medium': AsteroidSize(avg_radius=30, min_speed=1.8, max_speed=2.7, stroke_weight=2, points=50, index=1),
    'large': AsteroidSize(avg_radius=60, min_speed=1.2, max_speed=1.8, stroke_weight=3, points=20, index=2)
}

# die Größen, mit denen fliegende Untertassen spawnen können, und dazugehörige Weret (s. SaucerSize für die Bedeutungen der Attribute):
SAUCER_SIZES = {
    'small': SaucerSize(radius=15, stroke_weight=2, min_speed=2, max_speed=3, points=1000, aim=0.6, shoot_probability=1, bullet_lifetime=0.8, sound=0, index=0),
    'large': SaucerSize(radius=30, stroke_weight=3, min_speed=1.5, max_speed=2.25, points=200, aim=0.9, shoot_probability=0.5, bullet_lifetime=0.6, sound=1, index=1)
}

# die Schwierigkeiten
DIFFICULTIES = (
     # Die erste Schwierigkeit startet nach 0 Sekunden, und die Wahrscheinlichkeit, dass Asteroiden spawnen, liegt bei 0,6:
    Difficulty(0.6, 0),
    # Die erste Schwierigkeit startet nach 10 Sekunden, und die Wahrscheinlichkeit, dass Asteroiden spawnen, liegt bei 0,72:
    Difficulty(0.72, 10),
    Difficulty(0.9, 25), # Die dritte Schwierigkeit ...
    Difficulty(1.14, 45),
    Difficulty(1.44, 75),
    Difficulty(1.8, 120),
    Difficulty(2.16, 180),
    Difficulty(2.58, 300),
    Difficulty(3.06, 600)
)

# Die Menüs:
MAIN_MENU: Menu # das Hauptmenü
PAUSE_MENU: Menu # das Pausenmenü
GAME_OVER_MENU: Menu # das Spiel-ist-aus-Menü
SETTINGS_MENU: Menu # das Einstellungsmenü
RESET_ALL_CONFIRM_MENU: Menu # das Menü, in dem man gefragt wird, ob man wirklich alles löschen will
HIGH_SCORES_MENU: Menu # das Highscores-Menü


# Variablen

running: bool = True # so lange „wahr“, solange das Spiel läuft
game_over: bool = True # speichert, ob das Spiel aus ist
player: Player | None = None # der Spieler
fragment: Fragment | None = None # eventuell das Fragment des Spielers
asteroids: list[Asteroid] = [] # die Liste der Asteroiden
saucer: Saucer | None = None # die fliegende Untertasse
saucer_on_screen: bool # ob die fliegende Untertasse im Fenster ist
saucer_fragments: list[Fragment] = [] # die Fragmente fliegender Untertassen
fire_bullet: bool = False # ob man die Leertaste gedrückt hat, um zu schießen
bullets: list[Bullet] = [] # die Liste der Kugeln
saucer_bullets: list[SaucerBullet] = [] # die Liste der von fliegenden Untertassen abgefeuerten Kugeln
explosions: list[Explosion] = [] # die Liste der Explosionen (die beim Sprengen eines kleinen Asteroiden entstehen)
score: int
add_points: int = 0 # wie viele Punkte der Punktzahl hinzugefügt werden
ticks_since_last_points: int = 0 # die Anzahl von Ticks, die seit dem letzten Erhalten von Punkten vergangen sind
high_scores: list[HighScore] = [] # die Liste der Highscores (5 Highscores)
new_high_score: bool
lives: int
life_surface: pygame.Surface # 
playing_ticks: int = 0 # wie viele Ticks das aktuelle Spiel schon anhält
difficulty: Difficulty # die aktuelle Schwierigkeit
opened_menu: Menu | None # das aktuelle Menü
last_sound_tick: int = 0 # der letzte Tick, bei dem das Geräusch abgespielt wurde
play_beat_1: bool = True # ob als Nächstes der erste Beat gespielt werden soll


# Funktionen

# Die main()-Funktion
def main() -> None:
    global score, add_points

    pygame.init() # Pygame initialisieren
    pygame.font.init() # das Rendern von Schrift in Pygame initialisieren
    pygame.mixer.init() # den Soundmixer von Pygame initialisieren
    sounds.init() # die Geräusche in diesem Spiel initialisieren
    init() # dieses Spiel initialisieren
    
    screen = pygame.display.set_mode(SIZE) # das Fenster anlegen
    pygame.display.set_caption('Asteroids') # die Fensterüberschrift setzen

    clock = pygame.time.Clock() # mit dieser Uhr kann die Bildfrequenz geregelt werden

    # Spielloop
    while running:
        # Event-Handling
        for event in pygame.event.get():
            match event.type:
                case pygame.KEYDOWN:
                    handle_keydown_event(event)
                case pygame.KEYUP:
                    handle_keyup_event(event)
                case pygame.QUIT:
                    quit_game()
    
        update() # die Funktion update() aktualisiert alle Objekte, die im Fenster angezeigt werden
        render(screen) # die Funktion render() rendert alles, was angezeigt werden soll
        pygame.display.update() # das neu gerenderte Bild im Fenster anzeigen

        clock.tick(FPS) # das Programm so lange zur Ruhe legen, dass 60 FPS erreicht werden
        
    # Nach dem Spielloop:

    if game_over: # wenn das Spiel aus ist
        reset_game_state() # den Spielstand zurücksetzen, damit er nicht gespeichert wird
    elif add_points > 0: # wenn das Spiel noch läuft und noch Punkte zum Punktestand hinzuzufügen sind
        score += add_points # die Punkte hinzufügen
        add_points = 0 # keine Punkte mehr hinzuzufügen

    update_high_scores() # die Highscores aktualisieren

    save_game() # das Spiel speichern

    pygame.font.quit() # das Rendern von Schrift in Pygame beenden
    pygame.mixer.quit() # den Soundmixer von Pygame beenden
    pygame.quit() # das Spiel beenden


# Diese Funktion initialisiert das Spiel:
def init() -> None:
    init_constants() # alle Konstanten initalisieren
    load_game() # das Spiel aus der Datei „data.json“ laden
    get_and_set_difficulty() # die Schwierigkeit anhand der bereits gespielten Ticks einstellen
    render_life_surface() # die Oberfläche mit der Lebensanzeige rendern
    init_menus() # die Menüs initialisieren


# Diese Funktion wird einmal pro Tick aufgerufen und aktualisiert alles zu Aktualisierende:
def update() -> None:
    global game_over, player, fragment, asteroids, saucer, saucer_on_screen, saucer_fragments, fire_bullet, bullets
    global saucer_bullets, explosions, score, add_points, ticks_since_last_points, new_high_score, lives, playing_ticks

    if opened_menu in (None, GAME_OVER_MENU): # Wenn kein Menü oder das Spiel-ist-aus-Menü geöffnet ist
        if saucer is None:
            # mit einer Wahrscheinlichkeit, die 15-mal geringer ist als die Wahrscheinlichkeit, dass ein Asteroid spawnt,
            # eine neue fliegende Untertasse spawnen:
            if random.random() < difficulty.asteroid_spawn_chance / 15:
                saucer = new_saucer()
        else:
            saucer.update()
            if saucer_on_screen:
                saucer_on_screen = saucer.on_screen()
                if not saucer_on_screen: # wenn die fliegende Untertasse aus dem Fenster verschwindet
                    (sounds.SAUCERSMALL if saucer.size.sound == 0 else sounds.SAUCERBIG).stop() # ihr Geräusch beenden
                    saucer = None # die fliegende Untertasse despawnen
            else:
                saucer_on_screen = saucer.on_screen()
                # wenn der Spieler gerade spielt und eine fligende Untertasse im Fenster erscheint:
                if playing() and saucer_on_screen:
                    (sounds.SAUCERSMALL if saucer.size.sound == 0 else sounds.SAUCERBIG).play(-1) # ihr Geräusch abspielen

        for ls in (saucer_fragments, bullets, saucer_bullets, explosions):
            for obj in ls:
                obj.update() # alle Objekte in mehreren Listen aktualisieren

        # eine Liste von Asteroiden, die evtl. gleich durch Zerteilungen entstehen und die bald zur Asteroidenliste addiert wird
        asteroid_splits = []
        for a in asteroids:
            a.update() # jeden Asteroiden aktualisieren
            # prüfen, ob der Astroid von einer von einer fliegenden Untertasse abgeschossenen Kugel getroffen worden ist:
            a.check_hit(saucer_bullets, 2)
            a.check_hit(bullets, 1) # prüfen, ob der Asteroid von einer vom Spieler abgeschossenen Kugel getroffen worden ist
            if a.hit_by != 0: # wenn der Asteroid getroffen worden ist
                if a.hit_by == 1: # wenn der Asteroid vom Spieler getroffen worden ist
                    if add_points > 0:
                        score += add_points # zu addierende Punkte addieren
                    add_points = a.size.points # zu addierende Punkte auf die dazubekommenen Punkte setzen
                    # Wenn ein neuer Highscore erreicht worden ist:
                    if score + add_points > (high_scores[0].score if len(high_scores) > 0 else 0):
                        new_high_score = True 
                if playing(): # Es könnte auch das Spiel-ist-aus-Menü geöffnet sein
                    play_bang_sound(a.size)
                asteroid_splits += split_asteroid(a) # den Asteroiden zerteilen
                explosions.append(new_explosion(a.body.center.x, a.body.center.y, a.mot)) # eine neue Explosion erscheinen lassen

        if fragment is None:
            player.update() # wenn es kein Fragment gibt, gibt es einen Spieler, und dieser wird aktualisiert
            if fire_bullet:
                # die Kugel erscheint vorne am Raumschiff:
                bullet_pos = player.body.polar_coordinates[0].cartesian().add(player.body.center)
                
                bullet_angle = player.body.polar_coordinates[0].theta # die Richtung, in die die Kugel geschossen werden soll
                bullets.append(new_bullet(bullet_pos, bullet_angle)) # eine neue Kugel konstruieren und der Kugelliste hinzufügen
                sounds.FIRE.play()
                fire_bullet = False # nicht noch eine zweite Kugel schießen
        else:
            fragment.update() # das Fragment aktualisieren
            # wenn nicht das Spiel-ist-aus-Menü angezeigt wird und das Fragment eine Sekunde angezeigt wurde:
            if playing() and fragment.ticks == FPS:
                player = new_player(start_invincible=True) # neuen (anfangs unbesiegbaren) Spieler konstruieren
                fragment = None # das Fragment despawnen
                # Wenn der Spieler eine Vorwärts-Taste noch drückt, das Geräusch des Schubs fortsetzen:
                if pygame.key.get_pressed()[pygame.K_w] or pygame.key.get_pressed()[pygame.K_UP]:
                    sounds.THRUST.play(-1)
            fire_bullet = False # wenn es keinen Spieler gibt, kann nicht geschossen werden

        if saucer is not None:
            for a in asteroids:
                if saucer.body.collides_with_polygon(a.body): # wenn die fliegende Untertasse mit einem Asteroiden kollidiert:
                    saucer_die()
                    asteroid_splits += split_asteroid(a) # den Asteroiden sprengen
                    a.hit_by = 2
                    explosions.append(new_explosion(a.body.center.x, a.body.center.y, a.mot)) # eine neue Explosion erscheinen lassen
                    break # es müssen keine weiteren Kollisionen mit Asteroiden geprüft werden
            if saucer is not None: # wenn es immer noch einen fliegende Untertasse gibt
                saucer.check_hit(bullets, by=1)
                saucer.check_hit(saucer_bullets, by=2)
                if saucer.hit_by != 0: # wenn die fliegende Untertasse getroffen wurde
                    if saucer.hit_by == 1: # wenn die fliegende Untertasse vom Spieler getroffen wurde
                        if add_points > 0:
                            score += add_points # die zu addierenden Punkte zur Punktzahl addieren
                        # die nächsten zu addierenden Punkte anhand der Größe der fliegenden Untertasse setzen:
                        add_points = saucer.size.points 
                    saucer_die()
                if saucer is not None: # wenn es immer noch eine fliegende Untertasse gibt
                    # wenn es einen Spieler gibt und dieser nicht (mehr) unverwundbar ist und mit der fliegenden Untertasse
                    # kollidiert:
                    if player is not None and player.ticks >= INVINCIBILITY_TIME and player.body.collides_with_polygon(saucer.body):
                        player_die()
                        saucer_die()
                    # sonst: mit der Wahrscheinlichkeit, dass die fliegende Untertasse eine Kugel abschießt, die fliegende
                    # Untertasse eine Kugel abschießen lassen:
                    elif random.random() < saucer.size.shoot_probability:
                        # eine neue Fliegende-Untertasse-Kugel konstruieren und der Liste hinzufügen:
                        saucer_bullets.append(new_saucer_bullet())
                        if playing(): # es könnte auch das Spiel-ist-aus-Menü angezeigt werden
                            sounds.FIRE.play()

        # wenn der Spieler noch lebt er länger als die Unverwundbarkeitszeit lebt:
        if player is not None and player.ticks >= INVINCIBILITY_TIME:
            colliding_asteroid = player_collides_with_asteroid()
            if colliding_asteroid is not None: # wenn der Spieler mit einem Asteroiden kollidiert
                player_die()
                asteroid_splits += split_asteroid(colliding_asteroid)
                colliding_asteroid.hit_by = 2
                # eine neue Explosion erscheinen lassen:
                explosions.append(new_explosion(colliding_asteroid.body.center.x, colliding_asteroid.body.center.y,
                                                colliding_asteroid.mot))
                play_bang_sound(colliding_asteroid.size)
            else: # sonst: der Spieler lebt noch
                for b in saucer_bullets:
                    if player.body.vector_in(b.pos): # wenn der Spieler von einer Kugel von einer f. Untertasse getroffen wird
                        player_die()
                        sounds.BANGMEDIUM.play()
                        break # es muss nicht geprüft werden, ob der Spieler noch von weiteren Kugel getroffen wird

        asteroids += asteroid_splits # die Stücke des zerbrochenen Asteroiden der Asteroidenliste hinzufügen

        # mit der Wahrscheinlichkeit, dass bei der aktuellen Schwierigkeit ein Asteroid spawnt, einen Asteroiden spawnen:
        if random.random() < difficulty.asteroid_spawn_chance:
            asteroids.append(new_asteroid_no_args()) # einen neuen Asteroiden konstruieren und der Asteroidenliste hinzufügen

        # Die Liste der Asteroiden filtern: Es bleiben nur diejenigen übrig, die nicht getroffen worden sind
        # und nicht außerhalb des Fensters sind:
        asteroids = [a for a in asteroids if a.hit_by == 0 and not a.offscreen()]
        bullets = [b for b in bullets if not b.to_remove()] # alle zu entfernenden Kugeln vom Spieler entfernen
        saucer_bullets = [b for b in saucer_bullets if not b.to_remove()] # alle zu entfernenden Kugeln von f. Untertassen entfernen
        explosions = [e for e in explosions if not e.to_remove()] # alle zu entfernenden Explosionen entfernen
        saucer_fragments = [f for f in saucer_fragments if f.ticks < FPS] # alle zu entfernenden F.-Untertasse-Fragmente entfernen

        if playing():
            if add_points > 0: # wenn es Punkte gibt, die zur Punktzahl hinzukommen werden
                if ticks_since_last_points == FPS: # wenn seit dem Erzielen der Punkte eine Sekunde vergangen ist
                    score += add_points # die zu addierenden Punkte zur Punktzahl addieren
                    add_points = 0 # die zu addierenden Punkte auf 0 setzen
                    # die Anzahl von Ticks, die seit dem Erzielen der letzten Punkte vergangen sind, auf 0 setzen:
                    ticks_since_last_points = 0
                # die Anzahl von Tiks, die seit dem Erzielen der letzten Punkte vergangen sind, um eins erhöhen:
                ticks_since_last_points += 1
            beat()
            playing_ticks += 1 # die Anzahl von Ticks, wie lange das Spiel schon dauert, um eins erhöhen
            get_and_set_difficulty() # die Schwierigkeit ermitteln und setzen


# Diese Funktion kümmert sich um das Rendern von allem, was zu rendern ist:
def render(screen: pygame.Surface) -> None:
    if playing() or opened_menu.transparent:
        # alles rendern, was gerendert werden soll, wenn gerade ein Spiel läuft oder das geöffnete Menü transparent ist:
        screen.fill(Color.BLACK)
        if fragment is None:
            player.render(screen) # wenn es kein Fragment gibt, gibt es einen Spieler; diesen rendern
        else:
            fragment.render(screen)
        # alle Asteroiden, Kugeln, Kugeln fliegender Untertassen, Explosionen und Fragmente fliegender Untertassen rendern:
        for ls in (asteroids, bullets, saucer_bullets, explosions, saucer_fragments):
            for obj in ls:
                obj.render(screen)
        if saucer is not None:
            saucer.render(screen) # wenn es eine fliegende Untertasse gibt, diese rendern

    if playing():
        # alles rendern, was nur dann gerendert werden soll, wenn gerade ein Spiel läuft:
        score_surface = SCORE_FONT.render(str(score), True, Color.WHITE)
        screen.blit(score_surface, (15, 15)) # die Punktzahl rendern
        if add_points > 0: # wenn Punkte zur Punktzahl hinzukommen
            add_points_surface = SCORE_FONT.render('+%d' % add_points, True, Color.GREEN)
            # die Punkte, die zur Punktzahl hinzukommen, in Grün rendern:
            screen.blit(add_points_surface, (15 + score_surface.get_width(), 15)) 
        if new_high_score: # wenn der Spieler einen neuen Highscore aufgestellt hat
            # den neuen Highscore in Orange rendern:
            screen.blit(HIGHSCORE_FONT.render(str(score + add_points), True, Color.ORANGE), (15, 58))
        else:
            # den Highscore in weiß rendern:
            high_score_text = str(high_scores[0].score if len(high_scores) > 0 else (score + add_points))
            screen.blit(HIGHSCORE_FONT.render(high_score_text, True, Color.WHITE), (15, 58))
        for i in range(lives):
            screen.blit(life_surface, (15 + i * 22, 90)) # für jedes Leben ein Raumschiff auf das Fenster malen
    else:
        # alles rendern, was nur dann gerendert werden soll, wenn gerade KEIN Spiel läuft:
        opened_menu.render(screen)
        if opened_menu is PAUSE_MENU:
            for i in range(lives): # die Leben in der Mitte unter der Menüüberschrift anzeigen
                screen.blit(life_surface, ((WIDTH - 20 * lives - 2 * (lives - 1)) / 2 + i * 22, 205))


# Diese Funktion initialisiert alle Kontanten des Spiels, die noch nicht zugewiesen sind, außer die Menüs. (Das geschieht nur hier):
def init_constants() -> None:
    global ASTEROID_SPAWN_DISTANCE, ASTEROID_DESPAWN_DISTANCE, SCORE_FONT, HIGHSCORE_FONT, TITLE_FONT, TEXT_FONT, BUTTON_FONT
    
    # Die Entfernung von Asteroiden von der Mitte des Fensters bei ihrem Erscheinen
    # (die Entfernung zu den Ecken plus den durchschnittlichen Radius von Asteroiden mal 1,4):
    ASTEROID_SPAWN_DISTANCE = math.sqrt((WIDTH / 2) ** 2 + (HEIGHT / 2) ** 2) + ASTEROID_SIZES['large'].avg_radius * 1.4
    
    # der Despawn-Radius ist ein gutes Stück (25 Pixel) größer als der Spawn-Radius,
    # damit gerade erschienene Asteroiden nicht gleich wieder despawnen:
    ASTEROID_DESPAWN_DISTANCE = ASTEROID_SPAWN_DISTANCE + 25
    
    # Die Schriftarten laden:
    SCORE_FONT = pygame.font.Font('hyperspace-font/HyperspaceBold.ttf', 36)
    HIGHSCORE_FONT = pygame.font.Font('hyperspace-font/HyperspaceBold.ttf', 18)
    TITLE_FONT = pygame.font.Font('hyperspace-font/HyperspaceBold.ttf', 56)
    TEXT_FONT = pygame.font.Font('hyperspace-font/HyperspaceBold.ttf', 28)
    BUTTON_FONT = pygame.font.Font('hyperspace-font/HyperspaceBold.ttf', 28)
    
    # SCORE_FONT = pygame.font.SysFont('Impact', 36)
    # HIGHSCORE_FONT = pygame.font.SysFont('Impact', 18)
    # TITLE_FONT = pygame.font.SysFont('Impact', 56)
    # TEXT_FONT = pygame.font.SysFont('Impact', 28)
    # BUTTON_FONT = pygame.font.SysFont('Impact', 28)
    


# Diese Funktion initialisiert die Menüs:
def init_menus() -> None:
    global MAIN_MENU, PAUSE_MENU, GAME_OVER_MENU, SETTINGS_MENU, RESET_ALL_CONFIRM_MENU, HIGH_SCORES_MENU
    
    # das Hauptmenü initialisieren:
    MAIN_MENU = Menu(title='Asteroids', text=None, transparent=False, parent=None, button_data=(
        ButtonData(text='Continue', active=not game_over, on_action=continue_game),
        ButtonData(text='New Game', active=True, on_action=lambda: (set_timestamp_for_new_highscore(), new_game())),
        ButtonData(text='High Scores', active=True, on_action=open_high_scores_menu),
        ButtonData(text='Settings', active=True, on_action=lambda: open_menu(SETTINGS_MENU)),
        ButtonData(text='Quit Game', active=True, on_action=quit_game)
    ))
    
    # das Pausenmenü initialisieren:
    PAUSE_MENU = Menu(title='Paused', text=None, transparent=True, parent=None, button_data=(
        ButtonData(text='Continue', active=True, on_action=continue_game),
        ButtonData(text='Main Menu', active=True, on_action=lambda: (update_high_scores(), open_menu(MAIN_MENU)))
    ))
    
    # das Spiel-ist-aus-Menü initialisieren:
    GAME_OVER_MENU = Menu(title='Game Over!', text=None, transparent=True, parent=None, button_data=(
        ButtonData(text='New Game', active=True, on_action=new_game),
        ButtonData(text='Main Menu', active=True, on_action=lambda: open_menu(MAIN_MENU))
    ))
    
    # das Einstellungsmenü initialisieren:
    SETTINGS_MENU = Menu(title='Settings', text=None, transparent=False, parent=MAIN_MENU, button_data=(
        ButtonData(text='Reset Game State', active=True, on_action=reset_game_state_from_menu),
        ButtonData(text='Reset All', active=True, on_action=lambda: open_menu(RESET_ALL_CONFIRM_MENU)),
        ButtonData(text='Back', active=True, on_action=lambda: open_menu(MAIN_MENU))
    ))
    
    # das Menü, in dem man gefragt wird, ob man wirklich alles zurücksetzen will, initialisieren:
    RESET_ALL_CONFIRM_MENU = Menu(title='Confirm Reset', text='Are you sure you want to reset\nthe game state and high scores?',
                                  transparent=False, parent=SETTINGS_MENU, button_data=(
        ButtonData(text='Confirm', active=True, on_action=reset_all),
        ButtonData(text='Back', active=True, on_action=lambda: open_menu(SETTINGS_MENU))
    ))
    
    # das Highscore-Menü initialisieren:
    HIGH_SCORES_MENU = Menu(title='High Scores', text=None, transparent=False, parent=MAIN_MENU, button_data=(
        ButtonData(text='Back', active=True, on_action=lambda: open_menu(MAIN_MENU)),
    ))
    
    open_menu(MAIN_MENU) # das Hauptmenü als aktuelles Menü setzen


# Diese Funktion kümmert sich darum, dass zu den richtigen Zeitpunkten der Beat abgespielt wird:
def beat() -> None:
    global last_sound_tick, play_beat_1
    
    # das Intervall anhand der Spielzeit bestimmen:
    if playing_ticks <= FPS * 30:
        interval = (-2 / (FPS * 1.5)) * playing_ticks + FPS # in den ersten 30 Sekunden immer schneller
    else:
        interval = FPS / 3 # nach 30 Sekunden immer dreimal pro Sekunde

    # prüfen, ob es Zeit ist, das Geräusch abzuspielen:
    if playing_ticks - last_sound_tick >= interval:
        (sounds.BEAT1 if play_beat_1 else sounds.BEAT2).play() # den Beat abspielen
        play_beat_1 = not play_beat_1
        last_sound_tick = playing_ticks # den letzten Abspielzeitpunkt aktualisieren



# Diese Funktion öffnet ein Menü und wählt dessen obersten Button aus:
def open_menu(menu: Menu | None) -> None:
    global opened_menu
    opened_menu = menu
    if menu is not None:
        menu.select_top_button() # den obersten Button des geöffneten Menüs auswählen


# Diese Funktion aktualisiert und öffnet das Highscore-Menü
def open_high_scores_menu() -> None:
    HIGH_SCORES_MENU.set_text(high_scores_text(), update_buttons_y=True) # das Highscore-Menü aktualisieren
    open_menu(HIGH_SCORES_MENU)


# Diese Funktion setzt das Spiel fort:
def continue_game() -> None:
    open_menu(None) # das geöffnete Menü schließen
    if saucer is not None and saucer_on_screen: # wenn es eine fliegende Untertasse gibt, die sich auf dem Bildschirm befindet
        # das Geräusch der fliegenden Untertasse fortsetzen:
        sound = sounds.SAUCERSMALL if saucer.size.sound == 0 else sounds.SAUCERBIG
        sound.play(-1)


# Diese Funktion wird aufgerufen, wenn ein neues Spiel gestartet wird:
def new_game() -> None:
    global game_over, player, fragment, saucer, saucer_on_screen, fire_bullet, score, add_points, ticks_since_last_points
    global new_high_score, lives, playing_ticks, last_sound_tick, play_beat_1
    game_over = False
    player = new_player(start_invincible=False)
    fragment = None
    asteroids.clear() # die Liste der Asteroiden leeren
    for _ in range(3): # drei neue Asteroiden der Liste hinzufügen
        asteroids.append(new_asteroid_no_args())
    saucer = None
    saucer_on_screen = False
    saucer_fragments.clear() # die Liste der Fragmente fliegender Untertassen leeren
    fire_bullet = False
    bullets.clear() # die Liste der Kugeln leeren
    saucer_bullets.clear() # die Liste der Kugeln fliegender Untertassen leeren
    explosions.clear() # die Liste der Explosionen leeren
    score = 0
    add_points = 0
    ticks_since_last_points = 0 # die Anzahl von Ticks, seitdem das letzte Mal Punkte geholt wurden, auf 0 zurücksetzen
    new_high_score = False
    lives = 3
    playing_ticks = 0
    last_sound_tick = 0
    play_beat_1 = True
    get_and_set_difficulty() # die Schwierigkeit anhand der bereits gespielten Ticks einstellen
    open_menu(None)
    for b in (MAIN_MENU.buttons[0], SETTINGS_MENU.buttons[0], SETTINGS_MENU.buttons[1]): # Buttons in Menüs reaktivieren
        b.active = True


# Diese Funktion setzt den Spielstand zurück:
def reset_game_state() -> None:
    global game_over, player, fragment, saucer, saucer_on_screen, fire_bullet, score, add_points, ticks_since_last_points
    global new_high_score, lives, playing_ticks, difficulty
    game_over = True
    player = None
    fragment = None
    asteroids.clear() # die Liste der Asteroiden leeren
    saucer = None
    saucer_on_screen = False # wenn es keine fliegende Untertasse gibt, ist auch keine im Fenster
    saucer_fragments.clear() # die Liste der Fragmente fliegender Untertassen leeren
    saucer_bullets.clear() # die Liste der Kugeln fliegender Untertassen leeren
    fire_bullet = False
    bullets.clear() # die Liste der Kugeln leeren
    saucer_bullets.clear() # die Liste der Kugeln fliegender Untertassen leeren
    explosions.clear() # die Liste der Explosionen leeren
    score = 0
    add_points = 0
    ticks_since_last_points = 0 # die Anzahl von Ticks, seitdem das letzte Mal Punkte geholt wurden, auf 0 zurücksetzen 
    new_high_score = False
    lives = 0
    playing_ticks = 0 # 0 Ticks gespielt
    difficulty = None # keine Schwierigkeit


# Diese Menü wird aus einem Menü heraus aufgerufen und setzt den Spielstand zurück:
def reset_game_state_from_menu() -> None:
    reset_game_state() # den Spielstand zurücksetzen
    MAIN_MENU.buttons[0].active = False # den Button „Continue“ im Hauptmenü inaktiv setzen
    SETTINGS_MENU.deselect_all_buttons() # alle Buttons im Einstellungsmenü deselektieren
    SETTINGS_MENU.buttons[0].active = False # den Button „Reset Game State“ im Einstellungsmenü inaktiv setzen
    SETTINGS_MENU.buttons[2].selected = True # den Button „Back“ im Einstellungsmenü auswählen


# Diese Funktion setzt alles zurück, also die Highscores und den Spielstand
def reset_all() -> None:
    global high_scores
    reset_game_state()
    high_scores = []
    for b in (MAIN_MENU.buttons[0], SETTINGS_MENU.buttons[0], SETTINGS_MENU.buttons[1]):
        b.active = False
    open_menu(SETTINGS_MENU)


# Diese Funktion beendet das Spiel
def quit_game() -> None:
    global running
    running = False # die globale Variable, die speichert, ob das Spiel läuft, auf „falsch“ setzen


# Diese Funktion wird aufgerufen, wenn der Spieler sterben soll:
def player_die() -> None:
    global player, fragment, game_over, score, add_points, lives
    lives -= 1 # ein Leben abziehen
    if lives == 0:
        # Wenn Punkte zu addieren sind, diese addieren und auf 0 setzen
        if add_points > 0:
            score += add_points
            add_points = 0

        game_over = True
        
        # Das Spiel-ist-aus-Menü anpassen und anzeigen:
        GAME_OVER_MENU.set_text('%d%s' % (score, ' (new high score)' if new_high_score else ''), update_buttons_y=True)
        open_menu(GAME_OVER_MENU)
        
        MAIN_MENU.buttons[0].active = False # den Button „Continue“ im Hauptmenü deaktivieren
        update_high_scores() # die Highscores aktualisieren
        sounds.SAUCERSMALL.stop()
        sounds.SAUCERBIG.stop()
    fragment = new_fragment() # ein neues Fragment konstruieren und spawnen
    sounds.THRUST.stop()
    player = None # den Spieler despawnen
    

# Diese Funktion wird aufgerufen, wenn die fliegende Untertasse sterben soll:
def saucer_die() -> None:
    global saucer, saucer_on_screen
    if playing(): # Es könnte auch das Spiel-ist-aus-Menü angezeigt werden
        play_bang_sound(saucer.size) # je nach der Größe der fliegenden Untertasse ein Knallgeräusch abspielen
    saucer_fragments.append(new_saucer_fragment()) # das Fragment der fliegenden Untertasse der Liste hinzufügen
    saucer = None
    saucer_on_screen = False
    # beide Fliegende-Untertasse-Geräusche stoppen:
    sounds.SAUCERSMALL.stop()
    sounds.SAUCERBIG.stop()


# Diese Funktion aktualisiert die Highscores:
def update_high_scores() -> None:
    global high_scores
    if score > 0:
        if -1 in [h.timestamp for h in high_scores]: # wenn gerade ein Spiel läuft
            for (i, h) in enumerate(high_scores):
                if h.timestamp == -1 and score > h.score: # den Highscore des gerade laufenden Spiels finden
                    high_scores[i] = HighScore(score, int(time.time()) if game_over else -1) # den Highscore überschreiben
                    high_scores.sort(key=lambda h: h.score, reverse=True) # die Highscores sortieren
        else: # wenn gerade kein Spiel läuft
            high_scores.append(HighScore(score, int(time.time()) if game_over else -1))
            high_scores.sort(key=lambda h: h.score, reverse=True) # die Highscores absteigend nach Punktestand sortieren
            high_scores = high_scores[:5] # nur die ersten fünf Highscores behalten


# Diese Funktion setzt den Zeitstempel für einen neuen Highscore:
def set_timestamp_for_new_highscore() -> None:
    for h in high_scores:
        if h.timestamp == -1: # den Highscore des gerade laufenden Spiels finden
            h.timestamp = int(time.time()) # den aktuellen Zeitstempel setzen
            return # es kann nur einen Highscore im gerade laufenden Spiel geben


# Wenn der Spieler mit einem Asteroiden kollidiert, gibt diese Funktion diesen zurück (andernfalls None):
def player_collides_with_asteroid() -> Asteroid | None:
    for a in asteroids:
        if player.body.collides_with_polygon(a.body): # den ersten Asteroiden finden, der mit dem Spieler kollidiert
            return a
    return None # wenn kein Asteroid gefunden wurde, der mit dem Spieler kollidiert


# Diese Funktion konstruiert eine neue Linie und gibt sie zurück:
def new_line(a: Vector, b: Vector, mot: Vector, turning_angle: float, stroke_weight: int) -> Line:
    a_to_b = b.sub(a)
    center = a_to_b.mult(random.random()).add(a)
    center_to_a = to_polar(a.sub(center))
    center_to_b = to_polar(b.sub(center))
    mot = mot.add(PolarCoordinate(random.random() * 2 * math.pi, random.uniform(0.3, 0.45)).cartesian())
    rot = turning_angle + random.uniform(-0.045, 0.045)
    return Line(center, center_to_a, center_to_b, mot, rot, stroke_weight)


# Diese Funktion konstruiert ein neues Fragment für den Spieler und gibt es zurück:
def new_fragment() -> Fragment:
    vectors = player.body.cartesian()
    lines = [new_line(a=Vector(vectors[i].x, vectors[i].y),
                      b=Vector(vectors[(i + 1) % len(vectors)].x, vectors[(i + 1) % len(vectors)].y),
                      mot=player.mot, turning_angle=player.turning_angle, stroke_weight=2) for i in range(len(vectors))]
    return Fragment(lines, ticks=0)


# Diese Funktion konstruiert ein neues Fragment einer fliegenden Untertasse und gibt es zurück:
def new_saucer_fragment() -> Fragment:
    vectors = saucer.body.cartesian()
    lines = [new_line(Vector(vectors[i].x, vectors[i].y), Vector(vectors[(i + 1) % len(vectors)].x, vectors[(i + 1) % len(vectors)].y), saucer.mot, 0, saucer.size.stroke_weight) for i in range(len(vectors))]
    l1a = saucer.body.polar_coordinates[1].cartesian().add(saucer.body.center)
    l1b = saucer.body.polar_coordinates[6].cartesian().add(saucer.body.center)
    l2a = saucer.body.polar_coordinates[2].cartesian().add(saucer.body.center)
    l2b = saucer.body.polar_coordinates[5].cartesian().add(saucer.body.center)
    lines.append(new_line(Vector(l1a.x, l1a.y), Vector(l1b.x, l1b.y), saucer.mot, 0, saucer.size.stroke_weight))
    lines.append(new_line(Vector(l2a.x, l2a.y), Vector(l2b.x, l2b.y), saucer.mot, 0, saucer.size.stroke_weight))
    return Fragment(lines, 0)


# Diese Funktion konstruiert einen neuen Asteroiden und gibt ihn zurück:
def new_asteroid(size: AsteroidSize, pos: Vector, mot_angle: Vector) -> Asteroid:
    corners = random.randint(7, 11) # 7 bis 11 Ecken für den neuen Asteroiden
    angle = random.random() * 2 * math.pi / corners # der Winkel, mit dem die Generierung der Polarkoordinaten beginnt
    angle_play = 2 * math.pi / corners # der Spielraum für Winkel
    polar_coordinates = []

    # die Ecken konstruieren:
    for _ in range(corners):
        theta = angle + angle_play * random.random()
        radius = size.avg_radius * random.uniform(0.6, 1.4) # den durchschnittlichen Radius mit einer zufälligen Zahl in einer Spanne multiplizieren
        polar_coordinate = PolarCoordinate(theta, radius)
        polar_coordinates.append(polar_coordinate)
        angle += 2 * math.pi / corners # insgesamt ein voller Kreis
        
    body = Polygon(center=pos, polar_coordinates=tuple(polar_coordinates), stroke_weight=size.stroke_weight, visible=True)
    speed = random.uniform(size.min_speed, size.max_speed)
    mot = PolarCoordinate(mot_angle, speed).cartesian()
    rot = size.min_speed * random.uniform(-0.01, 0.01)

    return Asteroid(size, body, mot_angle, mot, rot, 0)


def new_asteroid_no_args() -> Asteroid:
    size = randsize() # eine zufällige Größe bestimmen
    spawn_angle = random.uniform(0.0, math.pi * 2) # Asteroiden erscheinen in einem Kreis um um das Fenter herum
    pos = PolarCoordinate(spawn_angle, ASTEROID_SPAWN_DISTANCE).cartesian().add(CENTER)
    mot_angle = spawn_angle + math.pi + random.uniform(-math.pi * 0.375, math.pi * 0.375)
    return new_asteroid(size, pos, mot_angle)


# Diese Funktion zerteilt einen Asteroiden in zwei Stücke, wenn er groß genug ist; sonst gibt sie eine leere Liste zurück:
def split_asteroid(asteroid: Asteroid) -> list[Asteroid]:
    if asteroid.size is ASTEROID_SIZES['large']:
        size = ASTEROID_SIZES['medium'] # wenn der Asteroid groß ist, sind die Stücke, in die er zerteilt wird, mittelgroß
    elif asteroid.size is ASTEROID_SIZES['medium']:
        size = ASTEROID_SIZES['small'] # wenn der Asteroid mittelgroß ist, sind die Stücke, in die er zerteilt wird, klein
    else: # wenn der Asteroid klein ist
        return []
    mot_angle_1 = asteroid.mot_angle - random.random() * math.pi / 4 # ein ähnlicher Winkel mit etwas Variation
    mot_angle_2 = asteroid.mot_angle + random.random() * math.pi / 4
    return [new_asteroid(size, asteroid.body.center, mot_angle_1), new_asteroid(size, asteroid.body.center, mot_angle_2)]


# Diese Funktion konstruiert einen neuen Spieler und gibt ihn zurück:
def new_player(start_invincible: bool) -> Player:
    ticks = 0 if start_invincible else INVINCIBILITY_TIME
    return Player(body=None, thrust=None, turning_angle=0.0, mot=None, ticks=ticks)


# Diese Funktion konstruiert eine fliegende Untertasse und gibt sie zurück:
def new_saucer() -> Saucer:
    # eine kleine fliegende Untertasse mit einer Wahrscheinlichkeit von 1/5; sonst eine große:
    size = SAUCER_SIZES['large'] if random.random() > 0.2 else SAUCER_SIZES['small']
    
    side = random.choices(range(4), weights=SIDE_PROBABILITIES)[0] # die Seite, an der die fliegende Untertasse erscheint
    
    match side:
        case 0: # obere Seite
            # eine zufällige Postion am oberen Rand:
            pos = Vector(random.uniform(-size.radius, WIDTH + size.radius), -size.radius)
            # ein zufälliger Winkel, der im Durchschnitt gerade nach unten geht:
            mot_angle = random.uniform(math.pi * 0.125, math.pi * 0.875)
        case 1: # rechte Seite
            # eine zufällige Position am rechten Rand:
            pos = Vector(WIDTH + size.radius, random.uniform(-size.radius, HEIGHT + size.radius))
            # ein zufälliger Winkel, der im Durchschnitt gerade nach links geht:
            mot_angle = random.uniform(math.pi * 0.625, math.pi * 1.375)
        case 2: # untere Seite
            # eine zufällige Position am unteren Rand:
            pos = Vector(random.uniform(-size.radius, WIDTH + size.radius), HEIGHT + size.radius)
            # ein zufälliger Winkel, der im Durchschnitt gerade nach oben geht:
            mot_angle = random.uniform(-math.pi * 0.875, -0.125)
        case 3: # linke Seite
            # eine zufällige Position am linken Rand:
            pos = Vector(-size.radius, random.uniform(-size.radius, HEIGHT + size.radius))
            # ein zufälliger Winkel, der im Durchschnitt gerade nach rechts geht:
            mot_angle = random.uniform(-math.pi * 0.375, math.pi * 0.375)
            
    # den Körper der fliegenden Untertasse mit all seinen Polarkoordinaten konstruieren:
    body = Polygon(center=pos, polar_coordinates=(
        PolarCoordinate(-math.pi * 0.4, size.radius * 0.6),
        PolarCoordinate(-math.pi * 0.07, size.radius * 0.47),
        PolarCoordinate(math.pi * 0.1, size.radius),
        PolarCoordinate(math.pi * 0.3, size.radius * 0.8),
        PolarCoordinate(math.pi * 0.7, size.radius * 0.8),
        PolarCoordinate(math.pi * 0.9, size.radius),
        PolarCoordinate(math.pi * 1.07, size.radius * 0.47),
        PolarCoordinate(math.pi * 1.4, size.radius * 0.6)
    ), stroke_weight=size.stroke_weight, visible=True)
    
    # die restlichen Werte der fliegenden Untertasse:
    speed = random.uniform(size.min_speed, size.max_speed)
    steps = random.randint(SAUCER_MIN_STEPS, SAUCER_MAX_STEPS)
    mot = PolarCoordinate(mot_angle, speed).cartesian() # die Bewegung der fliegenden Untertasse
    
    # die fliegende Untertasse konstruieren und zurückgeben:
    return Saucer(size, body, mot, speed, steps, 0, 0)    


# Diese Funktion konstruiert eine Kugel und gibt sie zurück:
def new_bullet(pos: Vector, angle: float) -> Bullet:
    mot = PolarCoordinate(angle, BULLET_SPEED).cartesian() # die Bewegung der neuen Kugel
    return Bullet(pos, mot) # die neue Kugel konstruieren und zurückgeben


def new_saucer_bullet() -> SaucerBullet:
    if player is None:
        # Wenn es keinen Spieler gibt, schießt die fliegende Untertasse in eine zufällige Richtung:
        saucer_fire_angle = random.random() * 2 * math.pi
    else:
        # Wenn es einen Spieler gibt, schießt die fliegende Untertasse auf ihn:
        saucer_fire_angle = math.atan2(player.body.center.y - saucer.body.center.y, player.body.center.x - saucer.body.center.x)
        saucer_fire_angle += random.uniform(-saucer.size.aim / 2, saucer.size.aim / 2) # die Zielgenauigkeit reduzieren
    
    # Die Kugel erscheint mit einem Abstand vom Radius der fliegenden Untertasse von dieser entfernt:
    saucer_bullet_pos = PolarCoordinate(saucer_fire_angle, saucer.size.radius).cartesian().add(saucer.body.center)
    
    saucer_bullet_mot = PolarCoordinate(saucer_fire_angle, BULLET_SPEED).cartesian() # die Bewegung der Kugel
    
    # die Kugel konstruieren und zurückgeben:
    return SaucerBullet(saucer_bullet_pos, saucer_bullet_mot, saucer.size.bullet_lifetime, 0)


# Diese Funktion konstruiert eine neue Explosion aus zwei Koordinaten und gibt sie zurück:
def new_explosion(x: float, y: float, mot: Vector) -> Explosion:
    particles = [new_particle(x, y, mot) for _ in range(random.randint(3, 5))] # 3 bis 5 Partikel in einer Liste
    return Explosion(particles) # die Explosion konstruieren und zurückgeben


# Diese Funktion konstruiert ein neues Partikel aus zwei Koordinaten und gibt es zurück:
def new_particle(x: float, y: float, mot: Vector) -> Particle:
    pos = Vector(x, y) # die Position des neuen Partikels
    # die Bewegung des neuen Partikels:
    mot = PolarCoordinate(random.random() * 2 * math.pi, random.uniform(0.3, 0.45)).cartesian().add(mot)
    ticks = 0 # Ein neues Partikel gibt es seit 0 Ticks
    death_ticks = random.randint(60, 90) # die Anzahl von Ticks, nach denen das Partikel verschwinden wird
    return Particle(pos, mot, ticks, death_ticks)


# Diese Funktion spielt ein Knallgeräusch ab:
def play_bang_sound(size: AsteroidSize | SaucerSize) -> None:
    match size.index:
        case 0:
            sounds.BANGSMALL.play()
        case 1:
            sounds.BANGMEDIUM.play()
        case 2:
            sounds.BANGLARGE.play()


# Diese Funktion verarbeitet ein Tastendruck-Event:
def handle_keydown_event(event: pygame.event.Event) -> None:
    match event.key:
        case pygame.K_SPACE: # wenn der Spieler die Leertaste gedrückt hat
            space_pressed()
        case pygame.K_RETURN: # wenn der Spieler die Entertaste gedrückt hat
            return_pressed()
        case pygame.K_ESCAPE: # wenn der Spieler die Escapetaste gedrückt hat
            escape_pressed()
        case pygame.K_UP: # wenn der Spieler die Pfeiltaste nach oben gedrückt hat
            up_arrow_or_w_pressed()
        case pygame.K_w: # wenn der Spieler die Taste W gedrückt hat
            up_arrow_or_w_pressed()
        case pygame.K_DOWN: # wenn der Spieler die Pfeiltaste nach unten gedrückt hat
            down_arrow_or_s_pressed()
        case pygame.K_s: # wenn der Spieler die Taste S gedrückt hat
            down_arrow_or_s_pressed()


# Diese Funktion wird aufgerufen, wenn der Spieler die Leertaste drückt:
def space_pressed() -> None:
    global fire_bullet
    if playing() and player is not None: # wenn der Spieler gerade spielt und es gerade einen Spieler gibt
        fire_bullet = True


# Diese Funktion wird aufgerufen, wenn der Spieler die Entertaste drückt:
def return_pressed() -> None:
    if not playing():
        opened_menu.action() # die Aktion des ausgewählten Buttons ausführen


# Diese Funktion wird aufgerufen, wenn der Spieler die Escapetaste drückt:
def escape_pressed() -> None:
    global score, add_points, opened_menu
    if playing(): # wenn der Spieler gerade im Spiel ist
        if add_points > 0: # Wenn Punkte zu addieren sind, diese addieren und sie auf 0 setzen
            score += add_points
            add_points = 0
        
        # das Pausenmenü aktualisieren und anzeigen:
        PAUSE_MENU.set_text('\n%d%s' % (score, ' (new high score)' if new_high_score else ''), update_buttons_y=True)
        open_menu(PAUSE_MENU)
        
        # alle Geräusche des Spielers und der fliegenden Untertasse stoppen:
        sounds.THRUST.stop()
        sounds.SAUCERBIG.stop()
        sounds.SAUCERSMALL.stop()
    elif opened_menu is PAUSE_MENU:
        continue_game() # wenn das geöffnete Menü das Pausenmenü ist, das Spiel fortsetzen
    elif opened_menu.parent is not None:
        open_menu(opened_menu.parent) # wenn das geöffnete Menü ein Elternmenü hat, dieses öffnen


# Diese Funktion wird aufgerufen, wenn der Spieler die Pfeiltaste nach oben oder die Taste W drückt:
def up_arrow_or_w_pressed() -> None:
    if playing(): # wenn der Spieler sich im Spiel befindet
        if player is not None: # wenn es einen Spieler (ein Raumschiff) gibt
            sounds.THRUST.play(-1) # das Geräusch des Schubs in Dauerschleife abspielen
    else: # wenn ein Menü geöffnet ist
        opened_menu.select_button_above() # den Button über dem ausgewählten Button auswählen


# Diese Funktion wird aufgerufen, wenn der Spieler die Pfeiltaste nach unten oder die Taste S drückt:
def down_arrow_or_s_pressed() -> None:
    if not playing(): # wenn der Spieler sich in einem Menü befindet
        opened_menu.select_button_below() # den Button unter dem ausgewählten Button auswählen


# Diese Funktion wird aufgerufen, wenn es ein Taste-losgelassen-Event gibt:
def handle_keyup_event(event: pygame.event.Event) -> None:
    if event.key in (pygame.K_w, pygame.K_UP): # wenn es die Taste W oder die Pfeiltaste nach oben ist
        sounds.THRUST.stop() # das Geräusch des Schubs stoppen


# Diese Funktion rendert die Oberfläche, auf der ein Raumschiff (repräsentiert ein Leben) angezeigt wird:
def render_life_surface() -> None:
    global life_surface
    
    life_surface = pygame.Surface((20, 24), pygame.SRCALPHA) # eine transparente Oberfläche
    
    # ein Polygon, das ein Raumschiff beschreibt, auf die Oberfläche rendern:
    Polygon(center=Vector(10, 12), polar_coordinates=(
        PolarCoordinate(-math.pi / 2, 12),
        PolarCoordinate(2 * math.pi * 0.14, 12),
        PolarCoordinate(2 * math.pi * 0.16, 7.2),
        PolarCoordinate(2 * math.pi * 0.34, 7.2),
        PolarCoordinate(2 * math.pi * 0.36, 12)
    ), stroke_weight=1, visible=True).render(life_surface)


# Diese Funktion ermittelt die aktuelle Schwierigkeit und setzt sie:
def get_and_set_difficulty() -> None:
    global difficulty
    for d in reversed(DIFFICULTIES): # die Schwierigkeiten rückwärts durchlaufen
        # wenn mindestens so viele Ticks vergangen sind wie die Ticks, bei denen die Schwierigkeit beginnt:
        if playing_ticks >= d.starts_at_ticks:
            difficulty = d # die Schwierigkeit setzen
            return # aus der Funktion springen, da die Schwierigkeit jetzt ermittelt wurde


# Diese Funktion wandelt einen Vektor in eine Polarkoordinate um:
def to_polar(vector: Vector) -> PolarCoordinate:
    angle = math.atan2(vector.y, vector.x) # der Winkel
    distance = math.sqrt(vector.x ** 2 + vector.y ** 2) # die Distanz
    return PolarCoordinate(angle, distance)


# Diese Funktion gibt eine zufällige Asteroidengröße zurück:
def randsize() -> AsteroidSize:
    return random.choice((ASTEROID_SIZES['small'], ASTEROID_SIZES['medium'], ASTEROID_SIZES['large']))
    

# Diese Funktion setzt den Text mit den Highscores zusammen und gibt ihn zurück:
def high_scores_text() -> str:
    # Diese Funktion wandelt einen Zeitstempel in einen String aus dem Datum und der Zeit um:
    def date_and_time_str(timestamp: int) -> str:
        dt = datetime.fromtimestamp(timestamp)
        date_str = dt.strftime('%m/%d/%Y')
        hour = dt.hour
        am_or_pm = 'a.m.' if hour < 12 else 'p.m.'
        if hour > 12:
            hour -= 12
        time_str = '%02d:%02d %s' % (hour, dt.minute, am_or_pm)
        return '%s %s' % (date_str, time_str)
    ordinal_suffixes = ['st', 'nd', 'rd', 'th', 'th']
    if len(high_scores) == 0:
        return 'No high scores yet'
    else:
        return '\n'.join('%d%s: %d (%s)' % (i + 1, ordinal_suffixes[i], h.score, 'playing' if h.timestamp == -1
                                            else date_and_time_str(h.timestamp)) for (i, h) in enumerate(high_scores))
    

# Diese Funktion gibt zurück, ob der Spieler sich gerade im Spiel befindet:
def playing() -> bool:
    return opened_menu is None # Der Spieler befindet sich im Spiel, wenn kein Menü geöffnet ist


# Diese Funktion lädt alle nötigen Spieldaten aus der Datei „data.json“:
def load_game() -> None:
    global game_over, saucer_on_screen, score, high_scores, new_high_score, lives, playing_ticks
    try:
        with open('data.json', 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return
    game_over = data['game_over']
    load_player(data['player'])
    load_fragment(data['fragment'])
    load_asteroids(data['asteroids'])
    load_saucer(data['saucer'])
    saucer_on_screen = data['saucer_on_screen']
    load_saucer_fragments(data['saucer_fragments'])
    load_bullets(data['bullets'])
    load_saucer_bullets(data['saucer_bullets'])
    load_explosions(data['explosions'])
    score = data['score']
    high_scores = [HighScore(d['score'], d['timestamp']) for d in data['high_scores']]
    new_high_score = data['new_high_score']
    lives = data['lives']
    playing_ticks = data['playing_ticks']


# Diese Funktion lädt den Spieler aus dem Dictionary „data“, das 
def load_player(data: dict[str, object] | None) -> None:
    global player
    if data is not None:
        body = load_polygon(data['body'])
        thrust = load_polygon(data['thrust'])
        turning_angle = data['turning_angle']
        mot = load_vector(data['motion'])
        ticks = data['ticks']
        player = Player(body, thrust, turning_angle, mot, ticks)


# Diese Funktion lädt das Fragment aus einem Dictionary, das aus „data.json“ stammt:
def load_fragment(data: dict[str, object] | None) -> None:
    global fragment
    if data is not None:
        lines = [load_line(d) for d in data['lines']]
        ticks = data['ticks']
        fragment = Fragment(lines, ticks)


# Diese Funktion lädt eine Linie aus einem Dictionary, das aus „data.json“ stammt, und gibt sie zurück:
def load_line(data: dict[str, object]) -> Line:
    center = load_vector(data['center'])
    center_to_a = load_polar(data['center_to_a'])
    center_to_b = load_polar(data['center_to_b'])
    mot = load_vector(data['motion'])
    rot = data['rotation']
    stroke_weight = data['stroke_weight']
    return Line(center, center_to_a, center_to_b, mot, rot, stroke_weight)


# Diese Funktion lädt die Liste der Asteroiden aus einem Dictionary, das aus „data.json“ stammt:
def load_asteroids(data: list[dict[str, object]]) -> None:
    global asteroids
    asteroids = [Asteroid(tuple(ASTEROID_SIZES.values())[d['size']], load_polygon(d['body']), d['motion_angle'],
                          load_vector(d['motion']), d['rotation'], d['hit_by']) for d in data]


# Diese Funktion lädt die fliegende Untertasse aus einem Dictionary, das aus „data.json“ stammt:
def load_saucer(data: dict[str, object] | None) -> None:
    global saucer
    if data is not None:
        size = tuple(SAUCER_SIZES.values())[data['size']] # die Größe ist im Dictionary als Index gespeichert
        body = load_polygon(data['body'])
        mot = load_vector(data['motion'])
        speed = data['speed']
        steps = data['steps']
        ticks = data['ticks']
        hit_by = data['hit_by']
        saucer = Saucer(size, body, mot, speed, steps, ticks, hit_by)


# Diese Funktion lädt die Liste der Fragmente fliegender Untertassen aus einem Dictionary, das aus „data.json“ stammt:
def load_saucer_fragments(data: list[dict[str, object]]) -> None:
    global saucer_fragments
    saucer_fragments = [Fragment([load_line(l) for l in d['lines']], d['ticks']) for d in data]


# Diese Funktion lädt die Liste der Kugeln vom Spieler aus einem Dictionary, das aus „data.json“ stammt:
def load_bullets(data: list[dict[str, object]]) -> None:
    global bullets
    bullets = [Bullet(load_vector(d['position']), load_vector(d['motion'])) for d in data]


# Diese Funktion lädt die Liste der Kugeln von fligenden Untertassen aus einem Dictionary, das aus „data.json“ stammt:
def load_saucer_bullets(data: list[dict[str, object]]) -> None:
    global saucer_bullets
    # die Kugeln fliegender Untertassen aus den Daten laden:
    saucer_bullets = [SaucerBullet(load_vector(d['position']), load_vector(d['motion']), d['lifetime'], d['ticks']) for d in data]


# Diese Funktion lädt die Liste der Explosionen aus einem Dictionary, das aus „data.json“ stammt:
def load_explosions(data: list[dict[str, object]]) -> None:
    global explosions
    # die Explosionen aus den Daten und daraus alle Partikel laden:
    explosions = [Explosion([Particle(load_vector(p['position']), load_vector(p['motion']), p['ticks'], p['lifetime'])
                             for p in d['particles']]) for d in data]


# Diese Funktion lädt ein Polygon aus einem Dictionary, das aus „data.json“ stammt:
def load_polygon(data: dict[str, object]) -> Polygon:
    center = load_vector(data['center'])
    polar_coordinates = tuple([load_polar(d) for d in data['polar_coordinates']])
    stroke_weight = data['stroke_weight']
    visible = data['visible']
    return Polygon(center, polar_coordinates, stroke_weight, visible)


# Diese Funktion lädt einen Vektor aus einem Dictionary, das aus „data.json“ stammt:
def load_vector(data: dict[str, float]) -> Vector:
    return Vector(data['x'], data['y'])


# Diese Funktion lädt eine Polarkoordinate aus einem Dictionary, das aus „data.json“ stammt:
def load_polar(data: dict[str, float]) -> PolarCoordinate:
    return PolarCoordinate(data['theta'], data['radius'])


# Diese Funktion speichert alle zu speichernden Daten in der Datei „data.json“:
def save_game() -> None:
    data = {
        'game_over': game_over,
        'player': None if player is None else player.to_dict(),
        'fragment': None if fragment is None else fragment.to_dict(),
        'asteroids': [a.to_dict() for a in asteroids],
        'saucer': None if saucer is None else saucer.to_dict(),
        'saucer_on_screen': saucer_on_screen,
        'saucer_fragments': [f.to_dict() for f in saucer_fragments],
        'bullets': [b.to_dict() for b in bullets],
        'saucer_bullets': [b.to_dict() for b in saucer_bullets],
        'explosions': [e.to_dict() for e in explosions],
        'score': score,
        'high_scores': [h.to_dict() for h in high_scores],
        'new_high_score': new_high_score,
        'lives': lives,
        'playing_ticks': playing_ticks
    }
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)


# Aufruf der main()-Funktion:
if __name__ == '__main__':
    main()