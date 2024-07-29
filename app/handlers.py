import json
import os
from aiogram import F, Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import database_helper as dbh
import app.keyboards as kb
from ticket_generator import gen_image

router = Router()


class Reg(StatesGroup):
    reg = State()
    name = State()
    surn = State()
    nick = State()
    menu = State()


class Admin(StatesGroup):
    get_admin = State()


class GenTicket(StatesGroup):
    uid_await = State()
    ticket_level = State()
    event_await = State()


class GenEvent(StatesGroup):
    title_await = State()
    date_await = State()
    description_await = State()
    image_await = State()


class AdminStatusEdit(StatesGroup):
    user_id_await = State()
    del_user_id = State()


# Загрузка токена из файла config.json
with open('data/config.json', 'r') as config_file:
    config = json.load(config_file)

bot = Bot(token=config['telegram']['api_token'])


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if dbh.find_user(user_id):
        photo = FSInputFile("image/109596.png")
        await message.answer(
            f"Привет.\nТвой ID: {message.from_user.id},\nИмя: {message.from_user.first_name}",
            reply_markup=kb.main)
    else:
        await state.set_state(Reg.name)
        await message.answer("Нет проблем? Бери AKADEM!\n"
                             "Тебя еще нет в нашей базе данных, которую мы обязательно продадим при первой возможности, поэтому, скорее регестрируйся!\n"
                             "\nНапиши мне свое имя!")


# РЕГИСТРАЦИЯ
@router.message(Reg.name)
async def input_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.surn)
    await message.answer(f"Супер, у Максима Беляева бы это не получилось\n"
                         "(он бы ввел Madara202HoudildoSuperMaxLife2)...\n"
                         f"\nТеперь напиши свою фамилию!")


@router.message(Reg.surn)
async def input_surname(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)
    await state.set_state(Reg.nick)
    await message.answer(f"Превосходно, теперь ты почти в AKADEM!\n"
                         "Осталось написать лишь ник, я в тебя верю!!!\n")


@router.message(Reg.nick)
async def input_nickname(message: Message, state: FSMContext):
    await state.update_data(nick=message.text)
    await state.set_state(Reg.menu)
    data = await state.get_data()
    dbh.register_user(message.from_user.id, data["name"], data["surname"],
                      data["nick"])
    await message.answer(f"Добро пожаловать в AKADEM!!!\n"
                         f"Это главное меню!\n", reply_markup=kb.main)


### СПИСОК БИЛЕТОВ (РАЗРАБОТКА)
@router.callback_query(F.data == "tickets")
async def callback_tickets(callback_query: CallbackQuery):
    list_tpu = dbh.find_ticket_by_user_id(callback_query.from_user.id)
    list_tickets = []
    list_events = []
    list_btns = []
    for i in range(len(list_tpu)):
        list_events.append(dbh.find_event_by_id(list_tpu[i][1]))
        list_tickets.append(dbh.find_ticket_by_id(list_tpu[i][0]))
    for i in range(len(list_tickets)):
        list_btns.append([list_tickets[i][0], list_tickets[i][1], list_events[i][1]])
    print(list_btns)
    tickets_keyboard = kb.generate_tickets_buttons(list_btns)
    if list_btns:
        mes = "Вот твои билеты:"
    else:
        mes = "Билетов пока нет, хнык-хнык :((\n\nПриобрести билеты можно у администратора @f4awh1le"
    await callback_query.message.edit_text(mes, reply_markup=tickets_keyboard)


@router.callback_query(F.data.startswith("ti_"))
async def callback_ticket_shower(callback_query: CallbackQuery):
    ticket_info = dbh.find_ticket_by_id(callback_query.data.lstrip("ti_"))
    user_info = dbh.find_user(callback_query.from_user.id)
    ticket = gen_image(ticket_info[1], user_info[1], user_info[2], user_info[3], user_info[0])
    photo = FSInputFile(f'image/ticket{user_info[0]}.jpg')
    await callback_query.message.answer_photo(photo, "Билетик", reply_markup=kb.back_from_photo)
    os.remove(f'image/ticket{user_info[0]}.jpg')


### АФИША СОБЫТИЙ (РАЗРАБОТКА)
@router.callback_query(F.data == "events")
async def callback_tickets(callback_query: CallbackQuery):
    events = dbh.get_events()
    for i in range(len(events)):
        print(events[i])
    await callback_query.message.edit_text("События", reply_markup=kb.events)


### СОЗДАНИЕ ИВЕНТА (ДОДЕЛАТЬ)
@router.callback_query(F.data == "gen_event")
async def callback_title_await(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(GenEvent.title_await)
    await callback_query.message.edit_text("||Эээх, бляяя\\!||\n\n"
                                           "Жду название ивента прямо в этот чатик <3",
                                           parse_mode='MarkdownV2', reply_markup=kb.back_to_op_main)


@router.message(GenEvent.title_await)
async def callback_date_await(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(GenEvent.date_await)
    await message.answer(
        f"Хорошо, ивент __{message.text}__\\. Когда он будет проходить?\n\nP\\.S\\. "
        f"Формат даты \\(__31\\.12\\.20024__\\)",
        parse_mode='MarkdownV2', reply_markup=kb.back_to_op_main)


@router.message(GenEvent.date_await)
async def callback_date_await(message: Message, state: FSMContext):
    await state.update_data(date=message.text)
    await state.set_state(GenEvent.description_await)
    await message.answer(f"Сейчас требуется написать описание ивента:",
                         parse_mode='MarkdownV2', reply_markup=kb.back_to_op_main)


@router.message(GenEvent.description_await)
async def callback_description_await(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(GenEvent.image_await)
    await message.answer(f"Хорошо, теперь можешь прислать картинку. Если ее не будет - пришли 0.")


@router.message(GenEvent.image_await)
async def callback_image_await(message: Message, state: FSMContext):
    data = await state.get_data()
    print(data)
    if message.text == "0":
        mes = f"{data["title"]}\n{data['date']}\n\n{data['description']}\n\nЕСЛИ ВСЕ ВЕРНО - НАЖМИ СОХРАНИТЬ!"
        await state.update_data(image='None')
        await message.answer(mes, reply_markup=kb.save_event)
    else:
        pass


@router.callback_query(F.data == "save_event")
async def callback_tickets(callback_query: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        dbh.generate_party(data["title"], data["date"], data["description"], data["image"])
        await callback_query.message.edit_text("Гений, ты успешно создал событие\\!",
                                               parse_mode='MarkdownV2', reply_markup=kb.admin_main)
    except Exception as e:
        print(e)


# ВЫДАЧА БИЛЕТОВ
@router.callback_query(F.data == "gen_ticket")
async def callback_uid_await(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(GenTicket.uid_await)
    await callback_query.message.edit_text("Уебок, пришли мне __UID__ того, кому надо выдапть билет\\!",
                                           parse_mode='MarkdownV2', reply_markup=kb.back_to_op_main)


@router.message(GenTicket.uid_await)
async def callback_event_await(message: Message, state: FSMContext):
    await state.update_data(uid=message.text)
    data = await state.get_data()
    await state.set_state(GenTicket.event_await)
    ticket_recipient = dbh.find_user(data["uid"])
    if ticket_recipient:
        await state.set_state(GenTicket.event_await)
        await message.answer(
            f"Отлично, ебанашка, получатель найден, сравни с тем, что тебе прислал покупателеь и"
            f" выбери ивент, на который выдать билет\\!\n\n__ПОЛУЧАТЕЛЬ:__\n\n"
            f"**__{ticket_recipient[1] + " " + ticket_recipient[2]}__** _aka_ {ticket_recipient[3]}\n"
            f"\n"
            f"UID: __{ticket_recipient[0]}__",
            parse_mode='MarkdownV2', reply_markup=kb.generate_event_buttons())

    else:
        await message.answer(
            "Такого юзера нет, пробуй еще раз:\\)\\)\\)\\)\n\nя СПЕЦИАЛЬНО не сделаю тут повторный ввод\\)\\)\\)\\)\\!",
            parse_mode='MarkdownV2', reply_markup=kb.back_to_op_main)


@router.callback_query(F.data.startswith("ev_"))
async def callback_ticket_type(callback_query: CallbackQuery, state: FSMContext):
    event_id = callback_query.data.lstrip("ev_")
    event = dbh.find_event_by_id(event_id)
    await state.update_data(event_id=event_id)
    await state.set_state(GenTicket.ticket_level)
    mes = f"{event_message_generator(event)}Какой <u>тип</u> билета надо выдать?"
    await callback_query.message.edit_text(mes, parse_mode='HTML', reply_markup=kb.ticket_type)


@router.callback_query(F.data.startswith("tick_t_"))
async def callback_ticket_vip(callback_query: CallbackQuery, state: FSMContext):
    ticket_type = int(callback_query.data.lstrip("tick_t_"))
    data = await state.get_data()
    ticket_id = dbh.generate_ticket(ticket_type)
    dbh.generate_ticket_party_user_aspect(ticket_id, data["event_id"], data["uid"])
    await callback_query.message.edit_text("Билет успешно создан и привязан к пользователю, "
                                           "он получил об этом уведомление!", reply_markup=kb.back_to_op_main)
    await bot.send_message(
        chat_id=data["uid"],
        text="Вы получили билет, скорее проверьте свои билеты\\!",
        parse_mode='MarkdownV2', reply_markup=kb.tickets_only
    )
    await state.clear()


# ЭХО ХЕНДЛЕР
@router.message()
async def echo_handler(message: Message, state: FSMContext) -> None:
    print(type(dbh.find_user(message.from_user.id)))
    if message.from_user.id in config["admins"]:
        if message.text.startswith("/op"):
            if message.text == "/op":
                await message.answer("Включен режим администратора!", reply_markup=kb.admin_main)
            else:
                op_id = message.text.split()[1]
                await state.set_state(AdminStatusEdit.user_id_await)
                await state.update_data(new_op_id=op_id)
                await callback_admin_status(message, state)
        elif message.text.startswith("/deop"):
            if message.text == "/deop":
                await message.answer("Статус администратора отключен!", reply_markup=kb.main)
            else:
                deop_id = message.text.split()[1]
                await state.set_state(AdminStatusEdit.del_user_id)
                await state.update_data(deop_id=deop_id)
                await callback_del_admin(message, state)
    elif dbh.find_user(message.from_user.id):
        photo = FSInputFile("image/109596.png")
        await message.answer(f"Привет.\nТвой ID: {message.from_user.id},\nИмя: {message.from_user.first_name}",
                             reply_markup=kb.main)
    else:
        await state.set_state(Reg.name)
        await message.answer("Нет проблем? Бери AKADEM!\n"
                             "Тебя еще нет в нашей базе данных, которую мы обязательно продадим при первой возможности, поэтому, скорее регестрируйся!\n"
                             "\nНапиши мне свое имя!")


### НАСТРОЙКИ (РАЗРАБОТКА)
@router.callback_query(F.data == "settings")
async def callback_settings(callback_query: CallbackQuery):
    await callback_query.message.edit_text("Настройки:", reply_markup=kb.settings)


# НАЗНАЧЕНИЕ АДМИНИСТРАТОРА
@router.message(AdminStatusEdit.user_id_await)
async def callback_admin_status(message: Message, state: FSMContext):
    admin_id = await state.get_data()
    data = dbh.find_user(admin_id["new_op_id"])
    try:
        if data[0] in config["admins"]:
            await message.answer("Этот пользователь уже является администратором.",
                                 reply_markup=kb.back_to_op_main)
        elif data:
            mess = "Вы уверены, что хотите назначить администратором пользователя:\n\n" + profile_message_generator(
                data)
            await message.answer(mess, reply_markup=kb.admin_invite, parse_mode="MarkdownV2")
    except Exception as e:
        print(e)


@router.callback_query(F.data == "yes_admin")
async def callback_reg_admin(callback_query: CallbackQuery, state: FSMContext):
    admin_id = await state.get_data()
    admin_id = int(admin_id["new_op_id"])
    config['admins'].append(admin_id)
    with open('data/config.json', 'w') as config_file:
        json.dump(config, config_file, indent=2)
    await callback_query.message.edit_text(
        "Вы успешно назначили администратора\\!",
        parse_mode='MarkdownV2',
        reply_markup=kb.back_to_op_main
    )
    await bot.send_message(
        chat_id=admin_id,
        text="Вы были назначены администратором\\!",
        parse_mode='MarkdownV2'
    )


# УДАЛЕНИЕ АДМИНИСТРАТОРА
@router.message(AdminStatusEdit.del_user_id)
async def callback_del_admin(message: Message, state: FSMContext):
    admin_id = await state.get_data()
    data = dbh.find_user(admin_id["deop_id"])
    try:
        if data[0] not in config["admins"]:
            await message.answer("Этот пользователь не является администратором.",
                                 reply_markup=kb.back_to_op_main)
        elif data:
            mess = "Вы уверены, что хотите лишить прав администратора пользователя:\n\n" + profile_message_generator(
                data)
            await message.answer(mess, reply_markup=kb.del_admin, parse_mode="MarkdownV2")
    except Exception as e:
        print(e)


@router.callback_query(F.data == "del_yes_admin")
async def callback_del_send_admin(callback_query: CallbackQuery, state: FSMContext):
    admin_id = await state.get_data()
    admin_id = int(admin_id["deop_id"])
    config['admins'].remove(admin_id)
    with open('data/config.json', 'w') as config_file:
        json.dump(config, config_file, indent=2)
    await callback_query.message.edit_text(
        "Вы успешно лишили администратора прав\\!",
        parse_mode='MarkdownV2', reply_markup=kb.back_to_op_main)
    # Отправка сообщения новому администратору
    await bot.send_message(
        chat_id=admin_id,
        text="Вы были лишены прав, теперь вы женщина\\!",
        parse_mode='MarkdownV2'
    )


# ВОЗВРАТЫ В МЕНЮ
@router.callback_query(F.data == "back_to_main")
async def callback_back_to_main(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.edit_text("Главное меню:", reply_markup=kb.main)


@router.callback_query(F.data == "back_to_op_main")
async def callback_back_to_main(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.edit_text("Админ, ебать Беляева в рот, меню:", reply_markup=kb.admin_main)


@router.callback_query(F.data == "back_from_photo")
async def callback_back_to_main(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await state.clear()
    # await callback_query.message.edit_text("Админ, ебать Беляева в рот, меню:", reply_markup=kb.admin_main)


# ПРОФИЛЬ
@router.callback_query(F.data == "profile")
async def callback_profile(callback_query: CallbackQuery):
    data = dbh.find_user(callback_query.from_user.id)
    formatted_text = (f'Твой профиль👤\n\\(его нужно переслать администратору '
                      f'для покупки билетов или с любым другим вопросом\\)\\!\n\n') + profile_message_generator(
        data)
    await callback_query.message.edit_text(formatted_text, parse_mode='MarkdownV2', reply_markup=kb.profile)


def profile_message_generator(data):
    formatted_text = (
        f'**__{data[1] + " " + data[2]}__** _aka_ {data[3]}\n'
        f'\n'
        f'UID: __{data[0]}__')
    return formatted_text


# СОЗДАНИЕ СООБЩЕНИЯ БИЛЕТА
def event_message_generator(data):
    formatted_text = f'''<b><u>{data[1]}</u></b>\n{data[2]}\n\n{data[5]}\n\n'''
    return formatted_text
