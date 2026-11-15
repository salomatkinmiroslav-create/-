# bot.py — весь бот в одном файле
import asyncio
import logging
import os
from html import escape

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

# ==================== КОНФИГ ====================
# Токен берётся из переменной окружения BOT_TOKEN.
# На Railway/Render добавьте её в Variables.
# Локально можно вписать строкой ниже (не публикуйте!):
# BOT_TOKEN = "123456789:AAH..."
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан. Добавьте переменную окружения BOT_TOKEN.")

# ==================== ДАННЫЕ ====================
CATALOG = {
    "movies": {
        "label": "🎬 Фильмы",
        "categories": {
            "comedy": {
                "label": "😂 Комедии",
                "items": [
                    {"title": "Иван Васильевич меняет профессию", "year": 1973, "rating": 8.9,
                     "description": "Инженер Тимофеев изобретает машину времени и случайно меняется местами с царём Иваном Грозным. Классика советской комедии."},
                    {"title": "Операция «Ы» и другие приключения Шурика", "year": 1965, "rating": 8.6,
                     "description": "Три новеллы о приключениях студента Шурика. Гайдай в лучшей форме."},
                    {"title": "Джентльмены", "year": 2019, "rating": 8.5,
                     "description": "Американский журналист вляпывается в разборки британского наркобизнеса. Стильный гай-ричиевский криминал."},
                    {"title": "Один дома", "year": 1990, "rating": 7.6,
                     "description": "Мальчик остаётся один дома и защищает его от двух незадачливых грабителей."},
                ],
            },
            "horror": {
                "label": "👻 Ужасы",
                "items": [
                    {"title": "Сияние", "year": 1980, "rating": 8.4,
                     "description": "Писатель с семьёй присматривает за пустующим отелем и медленно сходит с ума. Кубрик и Кинг в одном флаконе."},
                    {"title": "Реинкарнация", "year": 2018, "rating": 7.3,
                     "description": "После смерти бабушки в семье начинают происходить странные вещи. Медленный психологический хоррор."},
                    {"title": "Заклятие", "year": 2013, "rating": 7.0,
                     "description": "Пара исследователей паранормальных явлений сталкивается с самым жутким делом в своей практике."},
                    {"title": "Оно", "year": 2017, "rating": 7.3,
                     "description": "Дети из городка Дерри объединяются против клоуна-оборотня Пеннивайза."},
                ],
            },
            "action": {
                "label": "💥 Боевики",
                "items": [
                    {"title": "Терминатор 2: Судный день", "year": 1991, "rating": 8.6,
                     "description": "Кэмерон, Шварценеггер и жидкий металл. Эталон жанра, к которому до сих пор возвращаются."},
                    {"title": "Матрица", "year": 1999, "rating": 8.5,
                     "description": "Хакер Нео узнаёт, что мир вокруг — симуляция. Революция в спецэффектах и философии."},
                    {"title": "Джон Уик", "year": 2014, "rating": 7.4,
                     "description": "Бывший наёмник возвращается к делу, когда кто-то убивает его собаку. Хореография — отдельный вид искусства."},
                    {"title": "Безумный Макс: Дорога ярости", "year": 2015, "rating": 8.1,
                     "description": "Погоня длиной в целый фильм по пустоши. Практические эффекты и минимум диалогов."},
                ],
            },
            "scifi": {
                "label": "🚀 Фантастика",
                "items": [
                    {"title": "Интерстеллар", "year": 2014, "rating": 8.6,
                     "description": "Отец отправляется за горизонт событий, чтобы найти новый дом для человечества. Нолан разбирается с любовью и гравитацией."},
                    {"title": "Начало", "year": 2010, "rating": 8.6,
                     "description": "Кража идей из снов. Многоуровневый триллер с вращающимся коридором и финальным волчком."},
                    {"title": "Бегущий по лезвию 2049", "year": 2017, "rating": 8.0,
                     "description": "Блейд-раннер раскрывает тайну, способную изменить отношения людей и репликантов. Визуально безупречно."},
                    {"title": "Прибытие", "year": 2016, "rating": 7.9,
                     "description": "Лингвист пытается понять язык пришельцев — и заодно переосмысливает время и потерю."},
                ],
            },
            "drama": {
                "label": "🎭 Драмы",
                "items": [
                    {"title": "Побег из Шоушенка", "year": 1994, "rating": 9.1,
                     "description": "Двадцать лет надежды в тюрьме строгого режима. Фильм №1 в топах — и не зря."},
                    {"title": "Форрест Гамп", "year": 1994, "rating": 8.8,
                     "description": "Пробежал через полвека американской истории и остался хорошим человеком. Хэнкс в роли на все времена."},
                    {"title": "Зелёная миля", "year": 1999, "rating": 9.0,
                     "description": "Надзиратель в блоке смертников встречает заключённого с даром исцеления. Кино, которое выжимает."},
                    {"title": "Список Шиндлера", "year": 1993, "rating": 8.7,
                     "description": "Немецкий предприниматель спасает более тысячи евреев во время Холокоста. Чёрно-белая, тяжёлая, обязательная."},
                ],
            },
        },
    },
    "series": {
        "label": "📺 Сериалы",
        "categories": {
            "comedy": {
                "label": "😂 Комедии",
                "items": [
                    {"title": "Друзья", "year": 1994, "rating": 8.9,
                     "description": "Шестеро друзей, кофейня Central Perk и десять сезонов уюта. Классика ситкомов."},
                    {"title": "Офис", "year": 2005, "rating": 8.7,
                     "description": "Псевдодокументалка о буднях бумажного офиса в Скрэнтоне. Майкл Скотт — отдельный культурный код."},
                    {"title": "Теория Большого взрыва", "year": 2007, "rating": 8.2,
                     "description": "Физики-гики, соседка-актриса и много шуток про научпоп."},
                    {"title": "Бруклин 9-9", "year": 2013, "rating": 8.2,
                     "description": "Полицейский участок как большой детский сад. Тёплый и очень смешной."},
                ],
            },
            "detective": {
                "label": "🔍 Детективы",
                "items": [
                    {"title": "Шерлок", "year": 2010, "rating": 9.0,
                     "description": "Современная интерпретация Конан Дойла. Камбербэтч, Фриман и бешеная динамика."},
                    {"title": "Настоящий детектив", "year": 2014, "rating": 8.9,
                     "description": "Первый сезон: два детектива и 17 лет охоты за культом. Филигранно мрачно."},
                    {"title": "Менталист", "year": 2008, "rating": 8.0,
                     "description": "Бывший медиум помогает полиции Калифорнии раскрывать дела — лёгкий процедурал."},
                    {"title": "Кастл", "year": 2009, "rating": 7.9,
                     "description": "Писатель ходит на службу вместе с детективом ради вдохновения. Уютный процедурал на 8 сезонов."},
                ],
            },
            "scifi": {
                "label": "🚀 Фантастика",
                "items": [
                    {"title": "Чёрное зеркало", "year": 2011, "rating": 8.6,
                     "description": "Антология о том, как технологии жрут нас по одной серии за вечер. Лучше не залпом."},
                    {"title": "Очень странные дела", "year": 2016, "rating": 8.6,
                     "description": "Восьмидесятые, дети на великах, девочка с суперсилой и портал в изнанку."},
                    {"title": "Игра престолов", "year": 2011, "rating": 9.2,
                     "description": "Семь королевств, интриги и драконы. Финал не всем зашёл, но первые 6 сезонов — монументальны."},
                    {"title": "Мир Дикого Запада", "year": 2016, "rating": 8.5,
                     "description": "Парк с андроидами, где всё идёт не по сценарию. Головоломный сюжет и шикарный визуал."},
                ],
            },
            "drama": {
                "label": "🎭 Драмы",
                "items": [
                    {"title": "Во все тяжкие", "year": 2008, "rating": 9.5,
                     "description": "Учитель химии с раком лёгких решает сварить мет. Пять сезонов идеальной дуги персонажа."},
                    {"title": "Клан Сопрано", "year": 1999, "rating": 9.2,
                     "description": "Босс мафии Нью-Джерси ходит к психотерапевту. Родоначальник «серьёзной» телевизионной драмы."},
                    {"title": "Прослушка", "year": 2002, "rating": 9.3,
                     "description": "Балтимор во всех слоях — от улиц до редакций. Медленно, но навсегда."},
                    {"title": "Доктор Хаус", "year": 2004, "rating": 8.7,
                     "description": "Гениальный мизантроп-диагност и его команда. Медицинский процедурал с характером."},
                ],
            },
        },
    },
}

# ==================== КЛАВИАТУРЫ ====================
def main_menu_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=section["label"], callback_data=f"section:{key}")]
        for key, section in CATALOG.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def categories_kb(section_key: str) -> InlineKeyboardMarkup:
    cats = list(CATALOG[section_key]["categories"].items())
    rows = []
    for i in range(0, len(cats), 2):
        rows.append([
            InlineKeyboardButton(text=cat["label"], callback_data=f"cat:{section_key}:{key}")
            for key, cat in cats[i:i + 2]
        ])
    rows.append([InlineKeyboardButton(text="← Назад", callback_data="main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def back_kb(callback_data: str, text: str = "← Назад") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data=callback_data)]
    ])

# ==================== ХЕНДЛЕРЫ ====================
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        f"👋 Привет, <b>{escape(message.from_user.first_name)}</b>!\n\n"
        "Я помогу выбрать, что посмотреть вечером.\n"
        "Выбери раздел 👇",
        reply_markup=main_menu_kb(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Просто жми /start и выбирай категорию.\n"
        "В каждой категории — список тайтлов с годом, рейтингом и описанием."
    )


@router.callback_query(F.data == "main")
async def back_to_main(cb: CallbackQuery) -> None:
    await cb.message.edit_text("Выбери раздел 👇", reply_markup=main_menu_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("section:"))
async def show_section(cb: CallbackQuery) -> None:
    section_key = cb.data.split(":", 1)[1]
    section = CATALOG[section_key]
    await cb.message.edit_text(
        f"{section['label']}\n\nВыбери категорию 👇",
        reply_markup=categories_kb(section_key),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("cat:"))
async def show_category(cb: CallbackQuery) -> None:
    _, section_key, cat_key = cb.data.split(":")
    category = CATALOG[section_key]["categories"][cat_key]
    items = category["items"]

    await cb.message.edit_text(
        f"{category['label']}\n📦 Найдено: <b>{len(items)}</b>",
        reply_markup=back_kb(f"section:{section_key}", "← К категориям"),
    )

    for item in items:
        text = (
            f"<b>{escape(item['title'])}</b> ({item['year']})\n"
            f"⭐ <b>{item['rating']}</b>/10\n\n"
            f"{escape(item['description'])}"
        )
        await cb.message.answer(text)

    await cb.answer()


@router.message(F.text)
async def any_text(message: Message) -> None:
    await message.answer(
        "Я работаю по кнопкам 🙂 Жми /start, чтобы открыть меню.",
        reply_markup=main_menu_kb(),
    )

# ==================== ЗАПУСК ====================
async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")