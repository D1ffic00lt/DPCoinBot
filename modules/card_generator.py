import io
from math import e
import requests
from PIL import Image, ImageDraw, ImageFont

from additions import prepare_mask, divide_the_number


class CardGenerator(object):
    def __init__(
            self, avatar_url: str
    ):
        self.title_font = ImageFont.truetype("../static/fonts/UniSansBold.ttf", size=80)
        self.font = ImageFont.truetype("../static/fonts/UniSans.ttf", size=70)
        self.img = Image.new("RGBA", (1500, 900), "#323642")
        avatar = requests.get(avatar_url, stream=True)
        avatar = Image.open(io.BytesIO(avatar.content))
        avatar = avatar.convert("RGBA")
        avatar = avatar.resize((320, 320))
        avatar.putalpha(prepare_mask((320, 320), 4))

        self.img.alpha_composite(
            avatar, (70, 70)
        )

    def add_stats(
            self, name: str, wins: int = 0, loses: int = 0,
            minutes_in_voice: int = 0, messages: int = 0
    ):
        image_draw = ImageDraw.Draw(self.img)

        image_draw.text(
            (320 + 70 + 40, 70),
            name,
            font=self.title_font
        )
        image_draw.text(
            (60, 420),
            f"Wins: {divide_the_number(wins)}",
            font=self.font
        )
        image_draw.text(
            (60, 420 + 100),
            f"Loses: {divide_the_number(loses)}",
            font=self.font
        )
        image_draw.text(
            (60, 420 + 200),
            f"Minutes in voice: {divide_the_number(minutes_in_voice)}",
            font=self.font
        )
        image_draw.text(
            (60, 420 + 300),
            f"Messages: {divide_the_number(messages)}",
            font=self.font
        )

    def add_pins(
            self, verification: int = 0, developer: int = 0, coder: int = 0,
            fail: int = 0, wins_pin: int = 0, loses_pin: int = 0,
            coin: int = 0, minutes_pin: int = 0
    ):
        images = []
        if verification != 0:
            image = Image.open(f"../static/images/check/check_level_{verification}.png")
            image = image.convert("RGBA")
            image = image.resize((80, 80))
            images.append(image)
        if developer == 1:
            image = Image.open("../static/images/dev.png")
            image = image.convert("RGBA")
            image = image.resize((80, 80))
            images.append(image)
        if coder == 1:
            image = Image.open("../static/images/cmd.png")
            image = image.convert("RGBA")
            image = image.resize((80, 80))
            images.append(image)
        if fail == 1:
            image = Image.open("../static/images/fail.png")
            image = image.convert("RGBA")
            image = image.resize((80, 80))
            images.append(image)
        if coin == 1:
            image = Image.open("../static/images/coin.png")
            image = image.convert("RGBA")
            image = image.resize((80, 80))
            images.append(image)
        if minutes_pin != 0:
            image = Image.open(f"../static/images/minutes/{minutes_pin}_minutes.png")
            image = image.convert("RGBA")
            image = image.resize((80, 80))
            images.append(image)
        if wins_pin != 0:
            image = Image.open(f"../static/images/wins/{wins_pin}_wins.png")
            image = image.convert("RGBA")
            image = image.resize((80, 80))
            images.append(image)
        if loses_pin != 0:
            image = Image.open(f"../static/images/loses/{loses_pin}_loses.png")
            image = image.convert("RGBA")
            image = image.resize((80, 80))
            images.append(image)
        if len(images) != 0:
            x = 320 + 70 + 40
            for i in range(len(images)):
                self.img.alpha_composite(images[i], (x, 150))
                x += 100

    def drawProgressBar(self, progress, bg="black", fg="red"):
        x = 320 + 70 + 40
        y = 260
        w = 400
        h = 50
        draw = ImageDraw.Draw(self.img)
        draw.ellipse((x + w, y, x + h + w, y + h), fill=bg)
        draw.ellipse((x, y, x + h, y + h), fill=bg)
        draw.rectangle((x + (h / 2), y, x + w + (h / 2), y + h), fill=bg)

        w *= progress
        draw.ellipse((x + w, y, x + h + w, y + h), fill=fg)
        draw.ellipse((x, y, x + h, y + h), fill=fg)
        draw.rectangle((x + (h / 2), y, x + w + (h / 2), y + h), fill=fg)
        return draw
