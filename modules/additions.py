""" не смотрите сюда пж """
# -*- coding: utf-8 -*-
import random
import discord
import emoji
import os

from datetime import datetime
from typing import Callable, List, Any
from PIL import Image, ImageDraw
from vk_api import VkApi

from config import DATE_FORMAT

casino2 = {}


def write_log(text: str):
    if not os.path.exists(".logs"):
        os.mkdir(".logs")
    with open(".logs/develop_logs.dpcb", "a+", encoding="utf-8", errors="ignore") as file:
        file.write(text + "\n")


def prepare_mask(size, anti_alias: int = 2):
    mask = Image.new('L', (size[0] * anti_alias, size[1] * anti_alias))
    ImageDraw.Draw(mask).ellipse((0, 0) + mask.size, fill=255)
    return mask.resize(size, Image.ANTIALIAS)


def crop(im, s):
    w, h = im.size
    if w / s[0] - h / s[1] > 0:
        im = im.crop(((w - h) / 2, 0, (w + h) / 2, h))
    elif w / s[0] - h / s[1] < 0:
        im = im.crop((0, (h - w) / 2, w, (h + w) / 2))
    return im.resize(s, Image.ANTIALIAS)


def casino2ch(us_id: int) -> tuple:
    casino2[us_id] = []
    for i in range(4):
        casino2[us_id].append(random.randint(1, 2))
    random.shuffle(casino2[us_id])
    if random.randint(1, 9) == 1:
        casino2[us_id][0] = 2
    return casino2[us_id][0], casino2[us_id]


def get_time() -> str:
    return str(datetime.now().strftime(DATE_FORMAT))


def remove_emoji(text) -> str:
    return str(emoji.get_emoji_regexp().sub(u'', str(text)))


def divide_the_number(num):
    return '{:,}'.format(int(num)).replace('.', ' ')


def get_promo_code(num_chars) -> str:
    code_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    code = ''
    for i in range(0, num_chars):
        slice_start = random.randint(0, len(code_chars) - 1)
        code += code_chars[slice_start: slice_start + 1]
    return code


def ignore_exceptions(func: Callable) -> Callable:
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"[ERROR]: {e}")

    return decorator


def logging(func: Callable) -> Callable:
    def decorator(*args, **kwargs):
        with open(".logs/develop_logs.dpcb", "+a") as file:
            print(f"[{get_time()}] [INFO]: ", end="", file=file)
            print(f"[{get_time()}] [INFO]: ", end="")
        return func(*args, **kwargs)

    return decorator


def datetime_to_str(datetime_):
    return datetime.strptime(datetime_, DATE_FORMAT)


def create_emb(
        title: str, args: List[Any] = None,
        color: discord.Color = discord.Color.from_rgb(32, 34, 37),
        description: str = ""
) -> discord.Embed:
    emb = discord.Embed(title=title, colour=color, description=description)
    if args is not None:
        for row in list(args):
            emb.add_field(name=row["name"], value=row["value"], inline=row["inline"])
    return emb


def fail_rand(user_id):
    casino2[user_id] = []
    for i in range(7):  # 10
        casino2[user_id].append(float("%.2f" % (random.random() * random.randint(1, 2))))
    for i in range(10):  # 10
        casino2[user_id].append(float("%.2f" % (random.random() * (float(random.randint(1, 2))) / 4)))
    for i in range(4):
        casino2[user_id].append(float("%.2f" % (random.random() * random.randint(1, 5))))
    for i in range(3):  # 3
        casino2[user_id].append(float("%.2f" % (random.random() * random.randint(1, 10))))
    random.shuffle(casino2[user_id])
    return casino2[user_id][0], casino2[user_id]


def get_color(roles: List[discord.Role]):
    last_role = [role for role in roles][-1]
    if str(last_role) == "@everyone":
        return discord.Color.from_rgb(32, 34, 37)
    return last_role.color


def write_msg(user_id: int, message: str, vk: VkApi):
    vk.method(
        'messages.send',
        {
            'user_id': user_id,
            'message': message,
            'random_id': random.randint(1, 1000056785700)
        }
    )
