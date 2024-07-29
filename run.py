import asyncio
import logging
import json
from aiogram import Bot, Dispatcher
from database_helper import (create_party_table, create_ticket_party_user_table,
                             create_ticket_table, create_user_table)

# Загрузка токена из файла config.json
with open('data/config.json', 'r') as config_file:
    config = json.load(config_file)

from app.handlers import router

bot = Bot(token=config['telegram']['api_token'])
dp = Dispatcher()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    create_user_table()
    create_ticket_table()
    create_ticket_party_user_table()
    create_party_table()
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
