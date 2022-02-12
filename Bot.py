from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hbold, hlink
from aiogram.dispatcher.filters import Text
import logging
import os, time
from faunadb import query
from faunadb.client import FaunaClient
import asyncio

from database import user_exists, add_user, set_acive, get_users
from moodle import collect_data

bot_token = os.environ['BOT_TOKEN']
fauna_key = os.environ['FAUNAKEY']

bot = Bot(token=bot_token)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)
clientf = FaunaClient(fauna_key)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Hello")
    user_id = message.chat.id
    user_name = message.from_user.username
    if not user_exists(user_id):
        add_user(user_id, user_name)
        print(f"Запись в базу пользователя {user_name}")
    print("СТАРТ \n")


@dp.message_handler(commands=["run"])
async def run(message: types.Message):
    if message.from_user.id == 271175530:
        print("Начали рассылку")

        while True:
            answer_data = collect_data()
            if answer_data != False:
                # print(answer_data)
                if len(answer_data) != 0:
                    users = get_users()
                    for user in users:
                        try:
                            for tasks in answer_data:
                                for task in tasks:
                                    if 'description' in task.keys():
                                        message = f'{task["fullname"]}\n{task["name"]}\n{task["link"]}\n{task["description"]}'
                                        await bot.send_message(user['user_id'], message)
                                    elif 'link' not in task.keys():
                                        message = f'{task["fullname"]}\n{task["name"]}\n'
                                        await bot.send_message(user['user_id'], message)
                                    else:
                                        message = f'{task["fullname"]}\n{task["name"]}\n{task["link"]}'
                                        await bot.send_message(user['user_id'], message)

                            if int(user['active']) != 1:
                                set_acive(user['user_id'], 1)

                        except:
                            set_acive(user['user_id'], 0)
                            print("ERROR BLOCK \n")
                else:
                    print("НИЧЕГО НЕ ИЗМЕНИЛОСЬ")
                # await asyncio.sleep(20)
                await asyncio.sleep(3600)

            else:
                print("НИЧЕГО НЕ ИЗМЕНИЛОСЬ\n")
                await asyncio.sleep(20)


def main():
    executor.start_polling(dp)


if __name__ == "__main__":
    main()
