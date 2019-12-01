import snake_game_client
import config
import threading
from multiprocessing import Process
import time

threading.Thread(target=snake_game_client.SnakeClient, args=("1", "1", "localhost", config.PLAYER_1_LISTEN_PORT)).start()
threading.Thread(target=snake_game_client.SnakeClient, args=("1", "2", "localhost", config.PLAYER_2_LISTEN_PORT)).start()

# if __name__ == '__main__':
#     process1 = Process(target=snake_game_client.SnakeClient, args=("1", "1", "localhost", config.PLAYER_1_LISTEN_PORT))
#     process1.start()
#     process2 = Process(target=snake_game_client.SnakeClient, args=("1", "2", "localhost", config.PLAYER_2_LISTEN_PORT))
#     process2.start()
#     process1.join()
#     process2.join()
