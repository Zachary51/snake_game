import struct
import config


def create_game_message(id, name, port, type=config.CREATE_GAME):
    bytes_array = []
    bytes_type = struct.pack('!b', type)
    bytes_id_len = struct.pack('!b', len(id))
    bytes_name_len = struct.pack('!b', len(name))
    bytes_port = struct.pack('!h', port)
    bytes_id = str.encode(id)
    bytes_name = str.encode(name)
    bytes_array.append(bytes_type)
    bytes_array.append(bytes_id_len)
    bytes_array.append(bytes_name_len)
    bytes_array.append(bytes_id)
    bytes_array.append(bytes_name)
    bytes_array.append(bytes_port)
    return b''.join(bytes_array)


def join_game_message(id, name, port):
    return create_game_message(id, name, port, config.JOIN_GAME)


def change_direction_message(id, name, dir):
    bytes_array = []
    bytes_type = struct.pack('!b', config.CHANGE_DIRECTION)
    bytes_id_len = struct.pack('!b', len(id))
    bytes_name_len = struct.pack('!b', len(name))
    bytes_id = str.encode(id)
    bytes_name = str.encode(name)
    bytes_dir = struct.pack('!b', dir)
    bytes_array.append(bytes_type)
    bytes_array.append(bytes_id_len)
    bytes_array.append(bytes_name_len)
    bytes_array.append(bytes_id)
    bytes_array.append(bytes_name)
    bytes_array.append(bytes_dir)
    return b''.join(bytes_array)


def wait_for_user_msg(type=config.WAITING_FOR_2ND_USER):
    return struct.pack('!b', type)


def wait_for_start():
    return wait_for_user_msg(config.WAITING_FOR_GAME_START)


def game_over_message(result, winner):
    bytes_array = []
    bytes_type = struct.pack('!b', config.GAME_OVER)
    bytes_result = struct.pack('!b', result)
    bytes_name_len = struct.pack('!b', len(winner))
    bytes_name = str.encode(winner)
    bytes_array.append(bytes_type)
    bytes_array.append(bytes_result)
    bytes_array.append(bytes_name_len)
    bytes_array.append(bytes_name)
    return b''.join(bytes_array)


def create_bit_map(seq, apple_x, apple_y, snake1_x, snake1_y, snake2_x, snake2_y):
    bytes_array = []
    bytes_type = struct.pack('!b', config.BIT_MAP)
    bytes_seq = struct.pack('!b', seq)
    bytes_apple_row = struct.pack('!b', apple_y)
    bytes_apple_col = struct.pack('!b', apple_x)
    bytes_array.append(bytes_type)
    bytes_array.append(bytes_seq)
    bytes_array.append(bytes_apple_row)
    bytes_array.append(bytes_apple_col)
    # bitmap of snake 1
    for x in range(1, snake1_y):
        bytes_array.append(struct.pack('!b', 0))
    bytes_array.append(struct.pack('!b', snake1_x))
    for x in range(snake1_y+1, 33):
        bytes_array.append(struct.pack('!b', 0))
    # bitmap of snake 2
    for x in range(1, snake2_y):
        bytes_array.append(struct.pack('!b', 0))
    bytes_array.append(struct.pack('!b', snake2_x))
    for x in range(snake2_y+1, 33):
        bytes_array.append(struct.pack('!b', 0))
    return b''.join(bytes_array)









