import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# ====== Настройки =======
TELEGRAM_TOKEN = "7818975582:AAHCmUdYGpkGs-z79BmThYdHrxfwkRw48FE"
SPREADSHEET_ID = "104775550781290492911"  # берется из URL Google Sheets

# Области доступа для Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Подключаем сервисный аккаунт
creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

# Лист для заказов
ORDERS_SHEET_NAME = 'Заказы'

# ====== Инициализация бота =======
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# ====== Команда /start =======
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот службы доставки King Aqua.\n"
        "Используй команду /new_order для создания нового заказа."
    )

# ====== Команда /new_order =======
@dp.message_handler(commands=['new_order'])
async def cmd_new_order(message: types.Message):
    await message.answer("Отправь данные заказа в формате:\n"
                         "ФИО клиента; Телефон; Адрес; Кол-во бутылей; Стоимость бутыля")

    # Ждем следующий ответ с данными
    @dp.message_handler()
    async def process_order(msg: types.Message):
        try:
            data = msg.text.split(';')
            if len(data) != 5:
                await msg.answer("Неверный формат! Попробуй еще раз.")
                return

            fio = data[0].strip()
            phone = data[1].strip()
            address = data[2].strip()
            count = int(data[3].strip())
            price = float(data[4].strip())
            cost = count * price

            # Добавляем строку в Google Таблицу
            values = [[
                None,  # ID заказа (оставляем пустым, можно добавить потом)
                None,  # Дата - можно добавить авто
                None,  # Время
                fio,
                "физ",  # по умолчанию физ лицо
                phone,
                address,
                count,
                price,
                cost,
                None,  # способ оплаты
                None,  # назначено водителю
                "новый",
                None  # комментарии
            ]]
            body = {'values': values}
            sheet.values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{ORDERS_SHEET_NAME}!A1",
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()

            await msg.answer(f"Заказ клиента {fio} добавлен! Стоимость: {cost} руб.")
        except Exception as e:
            await msg.answer(f"Ошибка при добавлении заказа: {e}")

# ====== Запуск бота =======
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)