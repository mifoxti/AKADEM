import json

from PIL import Image, ImageDraw, ImageFont

with open('data/config.json', 'r') as config_file:
    config = json.load(config_file)


def gen_image(imtype, name, surname, nick, user_id):
    image = Image.open("image/" + config["image_types"][str(imtype)])
    font = ImageFont.truetype("font/font_pobeda.ttf", 360)
    drawer = ImageDraw.Draw(image)
    # ИМЯ
    drawer.text((1055, 2950), name, font=font, fill='white', align='center')
    # ФАМИЛИЯ
    drawer.text((1150, 3475), surname, font=font, fill='white', align='center')
    # НИК
    drawer.text((1055, 4900), nick, font=font, fill='white', align='center')
    scale_factor = 0.5
    new_width = int(image.width * scale_factor)
    new_height = int(image.height * scale_factor)

    # Измените размер изображения
    resized_img = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    resized_img.save(f'image/ticket{user_id}.jpg')
    return resized_img
