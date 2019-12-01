import socket
import random
import struct
import config
import bitmap
import packet
import single_snake
import threading
import time

udp_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
udp_server_socket.bind(('localhost', config.SERVER_LISTEN_PORT))
print("UDP server up and listening")


def _choose_random_pos():
    x = random.randrange(32)
    y = random.randrange(32)
    return x, y


class SnakeServer:
    """
    The server contains the main logic of this snake game
    """
    def __init__(self):
        self.bitmap_snake_1 = bitmap.Bitmap()
        self.bitmap_snake_2 = bitmap.Bitmap()
        self.player_1_port = ''
        self.player_2_port = ''
        self.dx, self.dy = 0, 1
        self.snake1_start_pos = _choose_random_pos()
        self.snake2_start_pos = _choose_random_pos()
        self.player_1_connected = False
        self.player_2_connected = False
        self.num_of_player = 0

        self.rows, self.cols = 32, 32
        self.snake_size = 20
        self.snake1 = single_snake.Snake(self.snake1_start_pos, self.rows, self.cols)
        self.snake2 = single_snake.Snake(self.snake2_start_pos, self.rows, self.cols)
        self.apple = _choose_random_pos()
        while self.apple == self.snake1_start_pos or self.apple == self.snake2_start_pos:
            self.apple = _choose_random_pos()

        self.game_over = False

    def _update_snake_body(self, direction, player):
        """
        Update the snake's body according to the direction change message
        :param direction: direction sent from client
        """
        if direction == config.RIGHT:
            self.dx, self.dy = 1, 0
        if direction == config.LEFT:
            self.dx, self.dy = -1, 0
        if direction == config.UP:
            self.dx, self.dy = 0, -1
        if direction == config.DOWN:
            self.dx, self.dy = 0, 1
        if player == 1:
            x, y = self.snake1.body[0]
            nx, ny = (x + self.dx) % self.cols, (y + self.dy) % self.rows
            if (nx, ny) in self.snake1.body or (nx, ny) in self.snake2.body:
                self.game_over = True
                return
            self.snake1.body.insert(0, (nx, ny))
            if not (nx, ny) == self.apple:
                self.snake1.body.pop()
            if self.snake1.head() == self.apple:
                while self.apple in self.snake1.body:
                    self.apple = _choose_random_pos()
        elif player == 2:
            x, y = self.snake2.body[0]
            nx, ny = (x + self.dx) % self.cols, (y + self.dy) % self.rows
            if (nx, ny) in self.snake2.body or (nx, ny) in self.snake1.body:
                self.game_over = True
                return
            self.snake2.body.insert(0, (nx, ny))
            if not (nx, ny) == self.apple:
                self.snake2.body.pop()
            if self.snake2.head() == self.apple:
                while self.apple in self.snake2.body:
                    self.apple = _choose_random_pos()

    def _generate_snake_bitmap(self):
        """
        Generate the snake bitmap for both 2 players based on the snake body queue
        :return:
        """
        for pos in self.snake1.body:
            x, y = pos
            self.bitmap_snake_1.set(x, y)
        for pos in self.snake2.body:
            x, y = pos
            self.bitmap_snake_2.set(x, y)
        return self.bitmap_snake_1.to_bit_map_array() + self.bitmap_snake_2.to_bit_map_array()


server = SnakeServer()

def process_handler():
    current_port = ''
    print('current num of player', server.num_of_player)
    msg = udp_server_socket.recvfrom(2048)[0]
    print('received', msg)
    if not server.player_1_connected and not server.player_2_connected:
        current_port = struct.unpack('!h', msg[-2:])[0]
        print('current port', current_port)
        print('player 1 port:', current_port)
        server.player_1_connected = True
        server.player_1_port = current_port
        server.num_of_player += 1
        waiting_for_component_msg = packet.wait_for_user_msg()
        print("Waiting message: ", waiting_for_component_msg)
        udp_server_socket.sendto(waiting_for_component_msg, ('localhost', current_port))
    if server.num_of_player == 1 and not server.player_2_connected:
        current_port = struct.unpack('!h', msg[-2:])[0]
        print('current port', current_port)
        print('player 2', current_port)
        server.player_2_port = current_port
        server.player_2_connected = True
        server.num_of_player += 1
    while server.num_of_player != 2:
        time.sleep(1)

    start_game_msg = packet.wait_for_start()
    print(start_game_msg)
    udp_server_socket.sendto(start_game_msg, ('localhost', current_port))
    print("game start!")

    while True:
        data = udp_server_socket.recvfrom(2048)
        port = data[1][1]
        data = data[0]
        player = 0
        if port == config.PLAYER_1_LISTEN_PORT:
            player = 1
            print("player", player)
        elif port == config.PLAYER_2_LISTEN_PORT:
            player = 2
            print("player", player)
        direction = data[-1]
        server._update_snake_body(direction, player)
        body = struct.pack('!b', config.BIT_MAP)
        body += server._generate_snake_bitmap()
        # Add the location of apple to the end of the bitmap message
        body += struct.pack('!h', server.apple[0])
        body += struct.pack('!h', server.apple[1])
        # Send the bitmap in the form of bytes to both players
        udp_server_socket.sendto(body, ('localhost', current_port))
        time.sleep(0.05)


threading.Thread(target=process_handler).start()
threading.Thread(target=process_handler).start()






