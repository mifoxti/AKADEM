import json

from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database_helper as dbh

with open('data/config.json', 'r') as config_file:
    config = json.load(config_file)
smiles = config["ticket_levels"]

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎉 Афиша", callback_data="events")],
    [InlineKeyboardButton(text="🎫 Билеты", callback_data="tickets"),
     InlineKeyboardButton(text="🛍️ Купить билет", url="https://t.me/gustova_04")],
    [InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
     InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")]
])

tickets = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
])

events = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️", callback_data="ev_back"),
     InlineKeyboardButton(text="➡️", callback_data="ev_next")],
    [InlineKeyboardButton(text="Назад", callback_data="back_to_main")]
])

profile = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
])

settings = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="🧑‍💻 Связь с разработчиком", url="https://t.me/mifoxti")],
                     [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
                     ])

back_to_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
])

back_to_op_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_op_main")]
])

save_event = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💾 Сохранить!", callback_data="save_event")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_from_photo")]
])

admin_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎫 Создать билет", callback_data="gen_ticket")],
    [InlineKeyboardButton(text="🎉 Создать событие", callback_data="gen_event"),
     InlineKeyboardButton(text="📢 Рассылка", callback_data="gen_broadcast")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="from_op_to_main"),
     InlineKeyboardButton(text="⚙️ Расширенные комманды", callback_data="more_com")]
])

ticket_type = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💎ᴠɪᴘ️", callback_data="tick_t_1"),
     InlineKeyboardButton(text="🎫standard", callback_data="tick_t_0")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_op_main")]
])

admin_invite = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❌️", callback_data="back_to_op_main"),
     InlineKeyboardButton(text="✅", callback_data="yes_admin")]
])

del_admin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❌️", callback_data="back_to_op_main"),
     InlineKeyboardButton(text="✅", callback_data="del_yes_admin")]
])

tickets_only = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎫 Билеты", callback_data="tickets")]
])

back_from_photo = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_from_photo")],
])

menu_from_poster = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💻 Главное меню", callback_data="menu_from_poster")],
])

menu_from_poster_photo = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💻 Главное меню", callback_data="back_to_main")],
])

menu_from_broadcast_texted = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💻 Главное меню", callback_data="from_op_to_main")],
])

broadcast_puller = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📢 Отправить!", callback_data="broadcast_pull")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_from_photo")]
])

more_op_comm = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🗑️ Удалить событие", callback_data="del_event")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_op_main")]
])

sure_delete = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅", callback_data="sure_delete")],
    [InlineKeyboardButton(text="❌️", callback_data="back_to_op_main")]
])

def generate_event_buttons(priq='ev'):
    partys = dbh.get_events()
    party_keyboard = InlineKeyboardBuilder()
    for party in partys:
        party_keyboard.add(InlineKeyboardButton(text=party[1], callback_data=f"{priq}_{party[0]}"))
    party_keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_op_main"))
    return party_keyboard.adjust(1).as_markup()


def generate_tickets_buttons(tickets):
    tickets_keyboard = InlineKeyboardBuilder()
    for ticket in tickets:
        tickets_keyboard.add(
            InlineKeyboardButton(text=smiles[str(ticket[1])] + ticket[2], callback_data=f"ti_{ticket[0]}"))
    tickets_keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    return tickets_keyboard.adjust(1).as_markup()


def generate_control_panel(prev, next):
    control = InlineKeyboardBuilder()
    # text="⬅️", callback_data="ev_back"
    # text="➡️", callback_data="ev_next"
    if prev:
        control.add(
            InlineKeyboardButton(text="⬅️", callback_data="ev_prev"))
    if next:
        control.add(
            InlineKeyboardButton(text="➡️", callback_data="ev_next"))
    control.add(InlineKeyboardButton(text="Назад", callback_data="back_to_main"))
    return control.adjust(prev + next if prev + next != 0 else 1).as_markup()
