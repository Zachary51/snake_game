import socket
import struct
import pygame
import time
import packet
import config
import threading
import sys

pygame.init()
class SnakeApp:
    def __init__(self):
        self.rows, self.cols = 32, 32
        self.snake_size = 20
        self.apple = (0, 0)
        self.surface = pygame.display.set_mode((self.cols * self.snake_size, self.rows * self.snake_size))
        pygame.display.set_caption("Snake Game")
        self.game_over = False

    def _draw_rect(self, pos, color):
        x, y = pos
        pygame.draw.rect(self.surface, color, (x*self.snake_size+1, y*self.snake_size+1, self.snake_size-2 , self.snake_size-2))

    def _bitmap_to_body(self, bitmap_snake):
        tmp_snake_1_body = []
        tmp_snake_2_body = []
        j = 0
        while j < 32:
            bits_row = bitmap_snake[j*4:j*4 + 4]
            bits_row = bin(struct.unpack('!I', bits_row)[0])
            str_bits = str(bits_row)[2:]
            str_bits = str_bits.zfill(32)
            for x in range(len(str_bits)):
                if str_bits[x] == '1':
                    tmp_snake_1_body.append((j, x))
            j += 1
        while j < 64:
            bits_row = bitmap_snake[j*4:j*4 + 4]
            bits_row = bin(struct.unpack('!I', bits_row)[0])
            str_bits = str(bits_row)[2:]
            str_bits = str_bits.zfill(32)
            for x in range(len(str_bits)):
                if str_bits[x] == '1':
                    tmp_snake_2_body.append((j-32, x))
            j += 1

        apple_x = struct.unpack('!h', bitmap_snake[-4:-2])[0]
        apple_y = struct.unpack('!h', bitmap_snake[-2:])[0]
        self.apple = (apple_x, apple_y)
        if (not self.apple == tmp_snake_1_body[0]) and len(tmp_snake_1_body) > 1:
            tmp_snake_1_body.pop()
        if (not self.apple == tmp_snake_2_body[0]) and len(tmp_snake_2_body) > 1:
            tmp_snake_2_body.pop()
        return tmp_snake_1_body, tmp_snake_2_body

    def _render(self, bitmap_snake):
        self.surface.fill(config.BLACK)
        self._draw_rect(self.apple, config.GREEN)
        snake1_body, snake2_body = self._bitmap_to_body(bitmap_snake)
        print("print", snake1_body)
        print("print", snake2_body)
        for pos in snake1_body:
            self._draw_rect(pos, config.RED)
        for pos in snake2_body:
            self._draw_rect(pos, config.BLUE)
        pygame.display.flip()

    def run_once(self, bitmap_snake):
        self._render(bitmap_snake)

    def _draw_game_over(self):
        pygame.display.flip()
        assert pygame.font.get_init()
        font = pygame.font.Font(None, 60)
        text = font.render("Game Over", True, config.BLUE)
        text_rect = text.get_rect()
        text_x = self.surface.get_width() / 2 - text_rect.width / 2
        text_y = self.surface.get_height() / 2 - text_rect.height / 2
        self.surface.blit(text, [text_x, text_y])
        pygame.display.flip()

    def _draw_waiting_for_component(self):
        pygame.display.flip()
        assert  pygame.font.get_init()
        font = pygame.font.Font(None, 60)
        text = font.render("WAITING FOR COMPONENT", True, config.BLUE)
        text_rect = text.get_rect()
        text_x = self.surface.get_width() / 2 - text_rect.width / 2
        text_y = self.surface.get_height() / 2 - text_rect.height / 2
        self.surface.blit(text, [text_x, text_y])
        pygame.display.flip()

    def _draw_ready_to_start(self):
        pygame.display.flip()
        assert pygame.font.get_init()
        font = pygame.font.Font(None, 60)
        text = font.render("GAME START", True, config.BLUE)
        text_rect = text.get_rect()
        text_x = self.surface.get_width() / 2 - text_rect.width / 2
        text_y = self.surface.get_height() / 2 - text_rect.height / 2
        self.surface.blit(text, [text_x, text_y])
        pygame.display.flip()


class SnakeClient:
    def __init__(self, game_id, nick_name, ip_address, port):
        # self.game_id = sys.argv[1]
        # self.nick_name = sys.argv[2]
        # self.ip_address = sys.argv[3]
        # self.port = sys.argv[4]
        self.game_id = game_id
        self.nick_name = nick_name
        self.ip_address = ip_address
        self.port = port
        self.bitmap_snake = b''
        self.udp_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.udp_client_socket.bind((self.ip_address, self.port))
        self.ready_to_start = False
        self._create_game()
        self.game = SnakeApp()
        threading.Thread(target=self._receiving_thread).start()
        threading.Thread(target=self._run_game_thread).start()

    def _get_dir(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            return config.RIGHT
        if keys[pygame.K_LEFT]:
            return config.LEFT
        if keys[pygame.K_UP]:
            return config.UP
        if keys[pygame.K_DOWN]:
            return config.DOWN

    def _receive_from_server(self):
        x = self.udp_client_socket.recvfrom(2048)[0]
        print("receive",x)
        return x

    def _send_to_server(self, direction):
        msg = packet.change_direction_message(self.game_id, self.nick_name, direction)
        print("send", msg)
        self.udp_client_socket.sendto(msg, (config.SERVER_IP_ADDRESS, config.SERVER_LISTEN_PORT))

    def _create_game(self):
        msg = packet.create_game_message(self.game_id, self.nick_name, self.port)
        print("send", msg)
        self.udp_client_socket.sendto(msg, (config.SERVER_IP_ADDRESS, config.SERVER_LISTEN_PORT))

    def _join_game(self):
        msg = packet.join_game_message(self.game_id, self.nick_name, self.port)
        self.udp_client_socket.sendto(msg, (config.SERVER_IP_ADDRESS, config.SERVER_LISTEN_PORT))

    # def _run_game(self):
    #     clock = pygame.time.Clock()
    #     fps = 10
    #     game = SnakeApp()
    #     msg_type = self._receive_from_server()
    #     if struct.unpack('!b', msg_type)[0] == config.WAITING_FOR_2ND_USER:
    #         print("draw waiting for component")
    #         game._draw_waiting_for_component()
    #         time.sleep(0.5)
    #     if struct.unpack('!b', msg_type)[0] == config.WAITING_FOR_GAME_START:
    #         print("draw waiting for ready to start")
    #         game._draw_ready_to_start()
    #
    #     while True:
    #         clock.tick(fps)
    #         for event in pygame.event.get():
    #             if event.type == pygame.QUIT:
    #                 pygame.quit()
    #                 game._draw_game_over()
    #         direction = self._get_dir()
    #         if direction is None:
    #             time.sleep(0.01)
    #             continue
    #         self._send_to_server(direction)
    #         time.sleep(0.05)
    #         self.bitmap_snake = self._receive_from_server()
    #         if len(self.bitmap_snake) >= 4:
    #             game.run_once(self.bitmap_snake)

    def _run_game_thread(self):
        clock = pygame.time.Clock()
        fps = 10
        while True:
            clock.tick(fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.game._draw_game_over()
            direction = self._get_dir()
            if direction is None:
                time.sleep(0.01)
            self._send_to_server(direction)
            time.sleep(0.05)

    def _receiving_thread(self):
        while True:
            msg = self._receive_from_server()
            if struct.unpack('!b', msg)[0] == config.WAITING_FOR_2ND_USER:
                print("draw waiting for component")
                self.game._draw_waiting_for_component()
                time.sleep(0.5)
            if struct.unpack('!b', msg)[0] == config.WAITING_FOR_GAME_START:
                print("draw waiting for ready to start")
                self.game._draw_ready_to_start()
            if struct.unpack('!b', msg)[0] == config.BIT_MAP:
                print("update the bitmap")
                self.bitmap_snake = msg[1:]
                if len(self.bitmap_snake) >= 4:
                    self.game.run_once(self.bitmap_snake)
            time.sleep(0.05)

    # def _run_multi_threads(self):
    #     threading.Thread(target=self._receiving_thread).start()
    #     threading.Thread(target=self._run_game_thread).start()













