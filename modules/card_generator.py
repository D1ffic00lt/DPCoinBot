import io
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
            minutes_in_voice: int = 0, messages: int = 0, xp: int = 0
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
        image_draw.text(
            (60, 420 + 400),
            f"XP: {divide_the_number(xp)}",
            font=self.font
        )

    def add_badges(
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
        if coin == 1:
            image = Image.open("../static/images/coin.png")
            image = image.convert("RGBA")
            image = image.resize((80, 80))
            images.append(image)
        if fail == 1:
            image = Image.open("../static/images/fail.png")
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
                self.img.alpha_composite(images[i], (x, 220))
                x += 100

    def draw_xp_bar(self, lvl, total_xp, xp):
        x = 320 + 70 + 40
        y = 150
        w = 400
        h = 50
        draw = ImageDraw.Draw(self.img)
        draw.text((x + 470, y), f"Total lvl: {lvl}", font=self.font)
        draw.ellipse((x + w, y, x + h + w, y + h), fill="grey")
        draw.ellipse((x, y, x + h, y + h), fill="grey")
        draw.rectangle((x + (h / 2), y, x + w + (h / 2), y + h), fill="grey")
        w *= (total_xp / xp)
        draw.ellipse((x + w, y, x + h + w, y + h), fill="aqua")
        draw.ellipse((x, y, x + h, y + h), fill="aqua")
        draw.rectangle((x + (h / 2), y, x + w + (h / 2), y + h), fill="aqua")
        return draw
