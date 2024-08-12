import json
import os

from aiogram import F, Router, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto

import app.keyboards as kb
import database_helper as dbh
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


class PosterViewer(StatesGroup):
    poster_id = State()
    return_to_show = State()


class BroadcastGen(StatesGroup):
    photo_await = State()
    message_await = State()
    release = State()


class DeleteEvent(StatesGroup):
    event_id = State()
    sure_delete = State()


# Загрузка токена из файла config.json
with open('data/config.json', 'r') as config_file:
    config = json.load(config_file)

bot = Bot(token=config['telegram']['api_token'])


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if dbh.find_user(user_id):
        photo = FSInputFile("image/None.jpg")
        await message.answer_photo(photo,
                                   f"Привет."
                                   f"\nТвой ID: {message.from_user.id},"
                                   f"\nИмя: {message.from_user.first_name}",
                                   reply_markup=kb.main)
    else:
        await state.set_state(Reg.name)
        await message.answer("Нет проблем? Бери AKADEM!\n"
                             "Тебя еще нет в нашей базе данных, которую мы обязательно продадим при первой возможности, поэтому, скорее регестрируйся!\n\nШУТКА\n\n"
                             "\nНапиши мне свое имя!")


# РЕГИСТРАЦИЯ
@router.message(Reg.name)
async def input_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.surn)
    await message.answer(f"Супер, у тебя получилось!\n"
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
    photo = FSInputFile("image/None.jpg")
    await state.clear()
    await message.answer_photo(photo,
                               f"Добро пожаловать в AKADEM!!!\n"
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
    tickets_keyboard = kb.generate_tickets_buttons(list_btns)
    if list_btns:
        mes = "Вот твои билеты:"
    else:
        mes = "Билетов пока нет, хнык-хнык :((\n\nПриобрести билеты можно у администратора @gustova_04"
    photo = FSInputFile("image/None.jpg")
    await bot.edit_message_media(chat_id=callback_query.message.chat.id,
                                 message_id=callback_query.message.message_id,
                                 media=InputMediaPhoto(media=photo, caption=mes),
                                 reply_markup=tickets_keyboard)


@router.callback_query(F.data.startswith("ti_"))
async def callback_ticket_shower(callback_query: CallbackQuery):
    ticket_info = dbh.find_ticket_by_id(callback_query.data.lstrip("ti_"))
    user_info = dbh.find_user(callback_query.from_user.id)
    gen_image(ticket_info[1], user_info[1], user_info[2], user_info[3], user_info[0])
    photo = FSInputFile(f'image/ticket{user_info[0]}.jpg')
    await bot.edit_message_media(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                                 media=InputMediaPhoto(media=photo, caption="Билетик"),
                                 reply_markup=kb.back_from_photo)
    os.remove(f'image/ticket{user_info[0]}.jpg')


### АФИША СОБЫТИЙ (РАЗРАБОТКА)
@router.callback_query(F.data == "events")
async def callback_events_poster(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(PosterViewer.poster_id)
    current_data = await state.get_data()
    events = dbh.get_events()
    max_id = len(events)
    current_id = 0
    if len(events) != 0:
        if not current_data:
            await state.update_data(current_id=0)
        else:
            current_id = current_data["current_id"]
        mes = (f"<b><u>{events[current_id][1]}</u></b>\n"
               f"<u>{events[current_id][2]}</u>\n\n"
               f"{events[current_id][5]}")
        event_keyboard = kb.generate_control_panel(1 if 0 - current_id < 0 else 0, 1 if max_id - current_id > 1 else 0)
        photo = FSInputFile(f"image/{events[current_id][4]}")
        await bot.edit_message_media(chat_id=callback_query.message.chat.id,
                                     message_id=callback_query.message.message_id,
                                     media=InputMediaPhoto(media=photo, caption=mes, parse_mode="HTML"),
                                     reply_markup=event_keyboard)

    else:
        mes = "Событий пока нет, хнык-хнык :("
        photo = FSInputFile("image/None.jpg")
        await bot.edit_message_media(chat_id=callback_query.message.chat.id,
                                     message_id=callback_query.message.message_id,
                                     media=InputMediaPhoto(media=photo, caption=mes, parse_mode="HTML"),
                                     reply_markup=kb.back_to_main)


@router.callback_query(F.data == "ev_next")
async def callback_next_event(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_id = data["current_id"] + 1
    await state.update_data(current_id=current_id)
    print(data)
    await callback_events_poster(callback_query, state)


@router.callback_query(F.data == "ev_prev")
async def callback_next_event(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_id = data["current_id"] - 1
    await state.update_data(current_id=current_id)
    print(data)
    await callback_events_poster(callback_query, state)


### УДАЛЕНИЕ ИВЕНТА
@router.callback_query(F.data == "more_com")
async def callback_more_admin_commands(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Расширенные комманды\n",
                                           parse_mode='MarkdownV2', reply_markup=kb.more_op_comm)


@router.callback_query(F.data == "del_event")
async def callback_del_event(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Выбери ивент, который хочешь удалить:\n",
                                           parse_mode='MarkdownV2', reply_markup=kb.generate_event_buttons(priq='dev'))


@router.callback_query(F.data.startswith("dev_"))
async def callback_dev_event(callback_query: CallbackQuery, state: FSMContext):
    event_id = int(callback_query.data.lstrip("dev_"))
    await state.set_state(DeleteEvent.sure_delete)
    await state.update_data(event_id=event_id)
    await callback_query.message.edit_text(
        "Вы уверены, что хотите удалить ивент и все связанные с ним билеты?\n"
        "Откатить изменение будет очень трудно!", reply_markup=kb.sure_delete)


@router.callback_query(F.data == "sure_delete")
async def callback_sure_delete(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    dbh.delete_event_by_id(data["event_id"])
    await callback_query.message.edit_text("Событие успешно удалено!", reply_markup=kb.back_to_op_main)


# СОЗДАНИЕ ИВЕНТА
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
    mes = f"{data['title']}\n{data['date']}\n\n{data['description']}\n\nЕСЛИ ВСЕ ВЕРНО - НАЖМИ СОХРАНИТЬ!"
    print(data)
    if message.text == "0":
        await state.update_data(image='None.jpg')
        await message.answer(mes, reply_markup=kb.save_event)
    elif message.text != "0":
        party_id = len(dbh.get_events()) + 1
        print(data)
        await message.bot.download(file=message.photo[-1].file_id, destination=f'image/event_{party_id}.jpg')
        await state.update_data(image=f'event_{party_id}.jpg')
        photo = FSInputFile(f"image/event_{party_id}.jpg")
        await message.answer_photo(photo, mes,
                                   reply_markup=kb.save_event)
        await state.update_data(is_photo="true")
        await state.set_state(BroadcastGen.message_await)


@router.callback_query(F.data == "save_event")
async def callback_tickets(callback_query: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        dbh.generate_party(data["title"], data["date"], data["description"], data["image"])
        await callback_query.message.answer("Гений, ты успешно создал событие\\!",
                                            parse_mode='MarkdownV2', reply_markup=kb.admin_main)
    except Exception as e:
        print(e)


# РАССЫЛКА
@router.callback_query(F.data == "gen_broadcast")
async def callback_gen_broadcast_photo(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(BroadcastGen.photo_await)
    print(state)
    await callback_query.message.edit_text("Можешь прислать картинку\\. Если ее не будет \\- пришли 0\\!",
                                           parse_mode='MarkdownV2', reply_markup=kb.back_to_op_main)


@router.message(BroadcastGen.photo_await)
async def callback_gen_broadcast_image(message: Message, state: FSMContext):
    if message.text != "0":
        await message.bot.download(file=message.photo[-1].file_id, destination='image/broadcast.png')
        await message.answer('Хорошо, теперь отправь текст рассылки.', reply_markup=kb.back_to_op_main)
        await state.update_data(is_photo="true")
        await state.set_state(BroadcastGen.message_await)
    elif message.text == "0":
        await message.answer('Хорошо, теперь отправь текст рассылки.', reply_markup=kb.back_to_op_main)
        await state.set_state(BroadcastGen.message_await)
        await state.update_data(is_photo="false")
    else:
        await message.answer('Какой-то ты кривой пиздец...', reply_markup=kb.admin_main)
        await state.clear()


@router.message(BroadcastGen.message_await)
async def callback_gen_broadcast_preview(message: Message, state: FSMContext):
    print(message.text)
    await state.update_data(message=message.text)
    data = await state.get_data()
    if data["is_photo"] == "true":
        photo = FSInputFile("image/broadcast.png")
        await message.answer_photo(photo, caption=message.text, reply_markup=kb.broadcast_puller)
    else:
        await message.answer(message.text, reply_markup=kb.broadcast_puller)


@router.callback_query(F.data == "broadcast_pull")
async def callback_gen_broadcast_pull(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    photo = FSInputFile("image/broadcast.png")
    is_photo = True if data["is_photo"] == "true" else False
    users = dbh.get_all_ids()
    for user in users:
        user_id = user[0]
        try:
            if is_photo:
                print(1)
                await bot.send_photo(chat_id=user_id, photo=photo, caption=data["message"],
                                     reply_markup=kb.menu_from_poster_photo)
            else:
                await bot.send_message(chat_id=user_id, text=data["message"],
                                       reply_markup=kb.menu_from_broadcast_texted)
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
    await state.clear()


@router.callback_query(F.data == "menu_from_poster")
async def callback_menu_from_poster_photo(callback_query: CallbackQuery, state: FSMContext):
    photo = FSInputFile("image/None.jpg")
    await callback_query.message.answer_photo(photo,
                                              f"Добро пожаловать в AKADEM!!!\n"
                                              f"Это главное меню!\n", reply_markup=kb.main)


# ВЫДАЧА БИЛЕТОВ
@router.callback_query(F.data == "gen_ticket")
async def callback_uid_await(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(GenTicket.uid_await)
    await callback_query.message.edit_text("Солнце, пришли мне __UID__ того, кому надо выдапть билет\\!",
                                           parse_mode='MarkdownV2', reply_markup=kb.back_to_op_main)


@router.message(GenTicket.uid_await)
async def callback_event_await(message: Message, state: FSMContext):
    await state.update_data(uid=message.text)
    data = await state.get_data()
    await state.set_state(GenTicket.event_await)
    ticket_recipient = dbh.find_user(data["uid"])

    if ticket_recipient:
        uid = ticket_recipient[0]
        await message.answer(
            f"Отлично, зайка, получатель найден, сравни с тем, что тебе прислал покупателеь и"
            f" выбери ивент, на который выдать билет!\n\n<u>ПОЛУЧАТЕЛЬ:</u>\n\n"
            f"<b>{ticket_recipient[1]} {ticket_recipient[2]}</b> <i>aka</i> {ticket_recipient[3]}\n"
            f"\n"
            f"UID: <u>{uid}</u>",
            parse_mode='HTML', reply_markup=kb.generate_event_buttons()
        )
    else:
        await message.answer(
            "Такого юзера нет, пробуй еще раз:)))\n\nя <b>СПЕЦИАЛЬНО</b> не сделаю тут повторный ввод!!!",
            parse_mode='HTML', reply_markup=kb.back_to_op_main
        )


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
    photo = FSInputFile("image/got_image.jpg")
    await bot.send_photo(
        chat_id=data["uid"], photo=photo,
        caption="Вы получили билет, скорее проверьте свои билеты\\!",
        parse_mode='MarkdownV2', reply_markup=kb.tickets_only
    )
    await state.clear()


# ЭХО ХЕНДЛЕР
@router.message()
async def echo_handler(message: Message, state: FSMContext) -> None:
    print(type(dbh.find_user(message.from_user.id)))
    if message.from_user.id in config["admins"] or message.from_user.id == 808305848:
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
                if str(deop_id) != "808305848":
                    await state.set_state(AdminStatusEdit.del_user_id)
                    await state.update_data(deop_id=deop_id)
                    await callback_del_admin(message, state)
                else:
                    await message.answer("Ты ниче не попутал?", reply_markup=kb.back_to_op_main)
    elif dbh.find_user(message.from_user.id):
        photo = FSInputFile("image/None.jpg")
        await message.answer_photo(photo,
                                   f"Добро пожаловать в AKADEM!!!\n"
                                   f"Это главное меню!\n", reply_markup=kb.main)
    else:
        await state.set_state(Reg.name)
        await message.answer("Нет проблем? Бери AKADEM!\n"
                             "Тебя еще нет в нашей базе данных, которую мы обязательно продадим при первой возможности, поэтому, скорее регистрируйся!\nШУТКА\n\n"
                             "\nНапиши мне свое имя!")


### НАСТРОЙКИ (РАЗРАБОТКА)
@router.callback_query(F.data == "settings")
async def callback_settings(callback_query: CallbackQuery):
    photo = FSInputFile("image/None.jpg")
    await bot.edit_message_media(chat_id=callback_query.message.chat.id,
                                 message_id=callback_query.message.message_id,
                                 media=InputMediaPhoto(media=photo,
                                                       caption="Пока ничего настроить нельзя, но скоро точно что\\-то будет\\!",
                                                       parse_mode='MarkdownV2'),
                                 reply_markup=kb.settings)


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
            await message.answer(mess, reply_markup=kb.admin_invite, parse_mode="HTML")
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
            await message.answer(mess, reply_markup=kb.del_admin, parse_mode="HTML")
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
        text="Вы были лишены прав администратора, сожалею\\!",
        parse_mode='MarkdownV2'
    )


# ВОЗВРАТЫ В МЕНЮ
@router.callback_query(F.data == "back_to_main")
async def callback_back_to_main(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    photo = FSInputFile("image/None.jpg")
    await bot.edit_message_media(chat_id=callback_query.message.chat.id,
                                 message_id=callback_query.message.message_id,
                                 media=InputMediaPhoto(media=photo, caption="Главное меню:",
                                                       parse_mode='MarkdownV2'),
                                 reply_markup=kb.main)


@router.callback_query(F.data == "back_to_op_main")
async def callback_back_to_main(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.edit_text("Админ меню:", reply_markup=kb.admin_main)


@router.callback_query(F.data == "from_op_to_main")
async def callback_back_to_main(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await state.clear()
    photo = FSInputFile("image/None.jpg")
    await callback_query.message.answer_photo(photo,
                                              f"Добро пожаловать в AKADEM!!!\n"
                                              f"Это главное меню!\n", reply_markup=kb.main)


@router.callback_query(F.data == "back_from_photo")
async def callback_back_to_main(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    photo = FSInputFile("image/None.jpg")
    await bot.edit_message_media(chat_id=callback_query.message.chat.id,
                                 message_id=callback_query.message.message_id,
                                 media=InputMediaPhoto(media=photo, caption="Админ меню:",
                                                       parse_mode='MarkdownV2'),
                                 reply_markup=kb.main)


# ПРОФИЛЬ
@router.callback_query(F.data == "profile")
async def callback_profile(callback_query: CallbackQuery):
    data = dbh.find_user(callback_query.from_user.id)
    formatted_text = (
                         'Твой профиль👤\n(его нужно переслать администратору '
                         'для покупки билетов или с любым другим вопросом)\n\n'
                     ) + profile_message_generator(data)

    photo = FSInputFile("image/None.jpg")

    await bot.edit_message_media(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        media=InputMediaPhoto(media=photo, caption=formatted_text, parse_mode='HTML'),
        reply_markup=kb.profile
    )


def profile_message_generator(data):
    formatted_text = (
        f'<b>{data[1]} {data[2]}</b> <i>aka</i> {data[3]}\n'
        f'\n'
        f'UID: <u>{data[0]}</u>'
    )
    return formatted_text


# СОЗДАНИЕ СООБЩЕНИЯ БИЛЕТА
def event_message_generator(data):
    formatted_text = f'''<b><u>{data[1]}</u></b>\n{data[2]}\n\n{data[5]}\n\n'''
    return formatted_text
