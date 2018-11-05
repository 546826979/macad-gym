##!/usr/bin/env python

# Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

# Keyboard controlling for CARLA. Please refer to client_example.py for a simpler
# and more documented example.

"""
Welcome to CARLA manual control.

Use ARROWS or WASD keys for control.

    W            : throttle
    S            : brake
    AD           : steer
    Q            : toggle reverse
    Space        : hand-brake
    P            : toggle autopilot

STARTING in a moment...
"""

from __future__ import print_function

import sys

sys.path.append(
    'PythonAPI/carla-0.9.0-py%d.%d-linux-x86_64.egg' % (3,6))

import carla

import argparse
import logging
import random
import time
import os

try:
    import pygame
    from pygame.locals import K_DOWN
    from pygame.locals import K_LEFT
    from pygame.locals import K_RIGHT
    from pygame.locals import K_SPACE
    from pygame.locals import K_UP
    from pygame.locals import K_a
    from pygame.locals import K_d
    from pygame.locals import K_p
    from pygame.locals import K_q
    from pygame.locals import K_r
    from pygame.locals import K_s
    from pygame.locals import K_w
except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')

try:
    import numpy as np
except ImportError:
    raise RuntimeError('cannot import numpy, make sure numpy package is installed')


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
START_POSITION = carla.Transform(carla.Location(x=180.0, y=199.0, z=40.0))  #
CAMERA_POSITION = carla.Transform(carla.Location(x=0.5, z=1.40))

from PythonAPI.converter import Converter 

class CarlaMap(object):
    def __init__(self, city, pixel_density=0.1643, node_density=50):
        dir_path = os.path.dirname(__file__)
        city_file = os.path.join(dir_path, city + '.txt')    
        self._converter = Converter(city_file, pixel_density, node_density)  
    def convert_to_pixel(self, input_data):
        """
        Receives a data type (Can Be Node or World )
        :param input_data: position in some coordinate
        :return: A node object
        """
        return self._converter.convert_to_pixel(input_data)

    def convert_to_world(self, input_data):
        """
        Receives a data type (Can Be Pixel or Node )
        :param input_data: position in some coordinate
        :return: A node object
        """
        return self._converter.convert_to_world(input_data)  
    

class CarlaGame(object):
    def __init__(self, args):
        self._client = carla.Client(args.host, args.port)
        self._display = None
        self._surface = None
        self._camera = None
        self._vehicle = None
        self._spawn_flag = args.spawn_flag 
        self.spawned_list = []
        self._autopilot_enabled = args.autopilot
        self._is_on_reverse = False
        self.test_map = CarlaMap('Town01')             #loading the map

    def execute(self):
        pygame.init() 
        try:
            self._display = pygame.display.set_mode(
                (WINDOW_WIDTH, WINDOW_HEIGHT),
                pygame.HWSURFACE | pygame.DOUBLEBUF)
            logging.debug('pygame started')

            world = self._client.get_world()
            blueprint = random.choice(world.get_blueprint_library().filter('vehicle'))
            self._vehicle = world.spawn_actor(blueprint, START_POSITION)
            self._vehicle.set_autopilot(self._autopilot_enabled)
            cam_blueprint = world.get_blueprint_library().find('sensor.camera')
            self._camera = world.spawn_actor(cam_blueprint, CAMERA_POSITION, attach_to=self._vehicle)

            self._camera.listen(lambda image: self._parse_image(image))

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                self._on_loop(event)
                self._on_render()
        finally:
            pygame.quit()
            if self._camera is not None:
                self._camera.destroy()
                self._camera = None
            if self._vehicle is not None:
                self._vehicle.destroy()
                self._vehicle = None

    def _parse_image(self, image):
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]
        array = array[:, :, ::-1]
        self._surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))

    def _on_loop(self,  event):
        autopilot = self._autopilot_enabled
        spawn_flag = self._spawn_flag 
        control = self._get_keyboard_control(pygame.key.get_pressed())
        if spawn_flag and event.type == pygame.MOUSEBUTTONUP:
#            mouse_x, mouse_y = event.pos
            benchmark_world_location = self._vehicle.get_location()
            real_location = [benchmark_world_location.x,benchmark_world_location.y, benchmark_world_location.z]
#            benchmark_image_location = self.test_map.convert_to_pixel(real_location)     

            world = self._client.get_world()
            blueprint = random.choice(world.get_blueprint_library().filter('vehicle')) 			
            transform = carla.Transform(carla.Location(x=benchmark_world_location.x - 10, y=benchmark_world_location.y, z=benchmark_world_location.z ), carla.Rotation(yaw=0.0))
            print('spawned vehicle at world location')
            print(real_location) 
            vehicle = world.try_spawn_actor(blueprint, transform)
            time.sleep(5)
            self.spawned_list.append(vehicle)

        if self.spawned_list:
            for vehicle in self.spawned_list:
                vehicle.set_autopilot(True)	

        if autopilot != self._autopilot_enabled:
            self._vehicle.set_autopilot(autopilot)
            self._autopilot_enabled = autopilot
        if not self._autopilot_enabled:
            self._vehicle.apply_control(control)
            if self.spawned_list:
                for vehicle in self.spawned_list:
                    vehicle.apply_control(control)

        self.spawned_list = []

    def _get_keyboard_control(self, keys):
        control = carla.VehicleControl()
        if keys[K_LEFT] or keys[K_a]:
            control.steer = -1.0
        if keys[K_RIGHT] or keys[K_d]:
            control.steer = 1.0
        if keys[K_UP] or keys[K_w]:
            control.throttle = 1.0
        if keys[K_DOWN] or keys[K_s]:
            control.brake = 1.0
        if keys[K_SPACE]:
            control.hand_brake = True
        if keys[K_q]:
            self._is_on_reverse = not self._is_on_reverse
        if keys[K_p]:
            self._autopilot_enabled = not self._autopilot_enabled
        control.reverse = self._is_on_reverse
        return control

    def _on_render(self):
        if self._surface is not None:
            self._display.blit(self._surface, (0, 0))
        pygame.display.flip()


def main():
    argparser = argparse.ArgumentParser(
        description='CARLA Manual Control Client')
    argparser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='debug',
        help='print debug information')
    argparser.add_argument(
        '--host',
        metavar='H',
        default='localhost',
        help='IP of the host server (default: localhost)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-a', '--autopilot',
        action='store_true',
        help='enable autopilot')
    argparser.add_argument(
        '-s', '--spawn_flag', 
        action='store_true',
        default=True,
        help='enable spawn vehicle')

    args = argparser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    logging.info('listening to server %s:%s', args.host, args.port)

    print(__doc__)

    while True:
        try:

            game = CarlaGame(args)
            game.execute()
            break

        except Exception as error:
            logging.error(error)
            time.sleep(1)


if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')
