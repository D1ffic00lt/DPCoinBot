import io
import math

import requests

from PIL import Image, ImageDraw, ImageFont

from units.additions import prepare_mask, divide_the_number


class CardGenerator(object):
    WINS_OFFSETS = 0.5
    LOSES_OFFSETS = 0.5
    MESSAGES_OFFSETS = 0.5
    MINUTES_IN_VOICE_OFFSETS = 0.05
    LVL_OFFSETS = 1
    ALL_OFFSETS = (
        WINS_OFFSETS + LOSES_OFFSETS +
        MESSAGES_OFFSETS + MINUTES_IN_VOICE_OFFSETS +
        LVL_OFFSETS
    )
    RANK_S_VALUE = 1
    RANK_DOUBLE_A_VALUE = 10
    RANK_A2_VALUE = 20
    RANK_A3_VALUE = 30
    RANK_B_VALUE = 50
    TOTAL_VALUES = (
        RANK_S_VALUE +
        RANK_DOUBLE_A_VALUE +
        RANK_A2_VALUE +
        RANK_A3_VALUE +
        RANK_B_VALUE
    )

    def __init__(
            self, avatar_url: str
    ):
        self.rang_data = {}
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
        self.rang_data["wins"] = wins
        self.rang_data["loses"] = loses
        self.rang_data["messages"] = messages
        self.rang_data["minutes_in_voice"] = minutes_in_voice
        image_draw = ImageDraw.Draw(self.img)
        if len(name) < 21:
            image_draw.text(
                (320 + 70 + 40, 70),
                name,
                font=self.title_font
            )
        else:
            image_draw.text(
                (320 + 70 + 40, 70),
                name,
                font=ImageFont.truetype("../static/fonts/UniSansBold.ttf", size=60)
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
        self.rang_data["lvl"] = lvl
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

    def normalization(self, mean):
        z = (self.ALL_OFFSETS - mean) / math.sqrt(2 * self.TOTAL_VALUES ** 2)
        t = 1 / (1 + 0.3275911 * abs(z))
        erf = 1 - (
            (
                (
                    (
                        1.061405429 * t + -1.453152027
                    ) * t + 1.421413741
                ) * t + -0.284496736
            ) * t + 0.254829592) * t * math.exp(-z * z)
        sign = 1 if z >= 0 else -1
        return (1 + sign * erf) / 2

    def add_rang(self):
        score = (
            self.rang_data["wins"] * self.WINS_OFFSETS +
            self.rang_data["loses"] * self.LOSES_OFFSETS +
            self.rang_data["messages"] * self.MESSAGES_OFFSETS +
            self.rang_data["minutes_in_voice"] * self.MINUTES_IN_VOICE_OFFSETS +
            self.rang_data["lvl"] * self.LVL_OFFSETS
        ) / 100
        score = self.normalization(score) * 100
        if score < self.RANK_S_VALUE:
            level = "S+"
        elif score < self.RANK_DOUBLE_A_VALUE:
            level = "S"
        elif score < self.RANK_A2_VALUE:
            level = "A++"
        elif score < self.RANK_A3_VALUE:
            level = "A+"
        else:
            level = "B+"
        x = 320 + 70 + 40 + 470 + 260
        y = 420 + 150
        total_size = 300
        size = 20
        draw = ImageDraw.Draw(self.img)
        draw.ellipse(
            (x, y, x + total_size, y + total_size),
            "#5494f4"
        )
        draw.pieslice(
            (x, y, x + total_size, y + total_size),
            start=270 - score * 10, end=270, fill="#dde5fb"
        )
        draw.ellipse(
            (x + size, y + size, x + total_size - size, y + total_size - size),
            "#323642"
        )
        if len(level) == 3:
            draw.text(
                (x + 35 + total_size / 6, y + 60 + total_size / 6),
                level, font=self.title_font
            )
        else:
            draw.text(
                (x + 60 + total_size / 6, y + 60 + total_size / 6),
                level, font=self.title_font
            )
        return level, score
