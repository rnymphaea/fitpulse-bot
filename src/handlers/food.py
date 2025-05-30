from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter
from aiogram.enums.parse_mode import ParseMode

from sqlalchemy.ext.asyncio import AsyncSession

from src.keyboards.food import select_option_keyboard, meals_keyboard, plot_keyboard
from src.keyboards.common import start_keyboard, confirmation_keyboard, cancel_keyboard
from src.storage.food import get_product, create_product, get_products, create_meal, get_today_meals, delete_all_user_food_data
from src.utils.plots import generate_nutrition_chart

food_router = Router()


class AddNewProduct(StatesGroup):
    name = State()
    calories = State()
    pfc = State()
    fiber = State()
    confirmation = State()


class AddNewMeal(StatesGroup):
    product = State()
    quantity = State()
    confirmation = State()


class Stats(StatesGroup):
    plot = State()


@food_router.callback_query(F.data == "food")
async def food(callback: CallbackQuery):
    kb = select_option_keyboard()
    await callback.message.edit_text("Выберите опцию", reply_markup=kb)


@food_router.callback_query(F.data == "add_plate")
async def add_product(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddNewProduct.name)
    kb = cancel_keyboard()
    await callback.message.answer("Введите название блюда", reply_markup=kb)
    await callback.message.delete()


@food_router.message(AddNewProduct.name)
async def process_product_name(message: Message, state: FSMContext, session: AsyncSession):
    telegram_id = message.from_user.id
    name = message.text
    kb = cancel_keyboard()
    exists = await get_product(session, telegram_id, name.lower())
    if exists:
        await message.answer("Блюдо уже есть в вашем списке!", reply_markup=kb)
    else:
        await message.answer("Введите количество калорий", reply_markup=kb)
        await state.update_data(name=name)
        await state.set_state(AddNewProduct.calories)


@food_router.message(AddNewProduct.calories)
async def process_product_calories(message: Message, state: FSMContext):
    kb = cancel_keyboard()
    try:
        calories = int(message.text)
        if calories <= 0:
            raise ValueError("calories must be positive!")
        await message.answer("Введите БЖУ на 100г блюда через пробел. \n Пример: 15.6 20.1 50.3", reply_markup=kb)
        await state.update_data(calories=calories)
        await state.set_state(AddNewProduct.pfc)

    except ValueError:
        await message.answer("Неверный формат данных! Введите положительное число.", reply_markup=kb)
    

@food_router.message(AddNewProduct.pfc)
async def process_product_pfc(message: Message, state: FSMContext):
    kb = cancel_keyboard()
    try:
        protein, fats, carbs = map(lambda x: int(x * 10), map(float, message.text.split()))
        if protein < 0 or fats < 0 or carbs < 0:
            raise ValueError("pfc must be non-zero!")
        await message.answer("Введите содержание пищевых волокон, если указано.", reply_markup=kb)
        await state.update_data(pfc=(protein, fats, carbs))
        await state.set_state(AddNewProduct.fiber)
    except ValueError:
        await message.answer("Неверный формат данных! \n Введите БЖУ на 100г блюда через пробел. \n Пример: 15.6 20.1 50.3", reply_markup=kb)
        

@food_router.message(AddNewProduct.fiber)
async def process_product_fiber(message: Message, state: FSMContext):
    try:
        fiber = int(float(message.text) * 10)
        if fiber < 0:
            raise ValueError("fiber must be non-zero!")
        info = await state.get_data()
        name = info['name']
        calories = info['calories']
        protein, fats, carbs = info['pfc']
        
        answer_text = (f"Вы хотите добавить следующее блюдо:\n"
            f"Название: {name}\n"
            f"Калории: {calories}\n"
            f"Белки: {protein / 10}г\n"
            f"Жиры: {fats / 10}г\n"
            f"Углеводы: {carbs / 10}г\n"
            f"Пищевые волокна: {fiber / 10}г\n?")
        kb = confirmation_keyboard()

        await message.answer(answer_text, reply_markup=kb)
        await state.update_data(fiber=fiber)
        await state.set_state(AddNewProduct.confirmation)
    except ValueError:
        await message.answer("Неверный формат данных! \n Введите целое число.")


@food_router.callback_query(
    F.data.in_(["confirmation_yes", "confirmation_no"]),
    StateFilter(AddNewProduct.confirmation)
)
async def process_product_confirmaion(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    if callback.data == "confirmation_no":
        await callback.message.answer("❌ Добавление отменено")
    else:
        info = await state.get_data()
        try: 
            await create_product(session, callback.from_user.id, info)
            await callback.message.answer("✅ Продукт успешно добавлен!")
        except Exception as e:
            await callback.message.answer("Что-то пошло не так при добавлении блюда в базу данных...")
            print(e)
            
    await callback.message.delete()
    kb = start_keyboard()
    await callback.message.answer("Выберите действие:", reply_markup=kb)
    await state.clear()
    await callback.answer()


@food_router.callback_query(F.data == "meals")
async def meals(callback: CallbackQuery):
    kb = meals_keyboard()
    await callback.message.edit_text("Какой приём пищи вы хотите добавить?", reply_markup=kb)


@food_router.callback_query(F.data.in_(["breakfast", "lunch", "dinner", "snack"]))
async def add_meal(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    translate = {'breakfast': 'Завтрак', 'lunch': 'Обед', 'dinner': 'Ужин', 'snack': 'Перекус'}
    products = await get_products(session, callback.from_user.id)
    data = {'meal_type': translate[callback.data], 'user_products': products, 'meal_products': []}
    await state.set_data(data)
    await state.set_state(AddNewMeal.product)
    text = "Введите номер того, что вы ели.\n\nСписок доступных продуктов:\n"
    count = 1
    for product in products:
        text += f" {count}. {product.name}\n"
        count += 1
    await callback.message.answer(text)


@food_router.message(AddNewMeal.product)
async def process_meal_name(message: Message, state: FSMContext):
    try:
        number = int(message.text)
        if number <= 0:
            raise ValueError("negative number")
        data = await state.get_data()
        try:
            product = data['user_products'][number-1]
            data['meal_products'].append([product.name, 0])
            await state.set_state(AddNewMeal.quantity)
            await state.set_data(data)
            kb = cancel_keyboard()
            await message.answer(f"Укажите, сколько вы съели блюда <b>{product.name}</b> в граммах", reply_markup=kb, parse_mode=ParseMode.HTML)
        except IndexError:
            await message.answer("Вашего номера нет в списке")
    except ValueError:
        await message.answer("Введите положительное число - номер блюда")


@food_router.callback_query(
    F.data == 'cancel',
    StateFilter(AddNewProduct.name, AddNewProduct.calories, AddNewProduct.pfc, AddNewProduct.fiber,
                AddNewMeal.quantity)
)
async def process_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("❌ Добавление отменено")
    kb = start_keyboard()
    await callback.message.answer("Выберите опцию", reply_markup=kb)
    await callback.message.edit_text(callback.message.text)
    await state.clear()
    await callback.answer()


@food_router.message(AddNewMeal.quantity)
async def process_meal_quantity(message: Message, state: FSMContext):
    try: 
        quantity = int(message.text)
        if quantity <= 0:
            raise ValueError("negative quantity")
        kb = cancel_keyboard()
        answer_text = "Если хотите ввести ещё блюдо, выбрите одно из списка, если нет - нажмите кнопку <b><i>Отмена</i></b>:\n"
        data = await state.get_data()
        data['meal_products'][-1][-1] = quantity 
        for i in range(len(data['user_products'])):
            product = data['user_products'][i]
            answer_text += f"{i+1}. {product.name}\n"
        await message.answer(answer_text, reply_markup=kb, parse_mode=ParseMode.HTML)
        await state.set_state(AddNewMeal.product)
        
    except ValueError:
        await message.answer("Введите положительно число - количество грамм")



@food_router.callback_query(
    F.data == 'cancel',
    StateFilter(AddNewMeal.product)
)
async def print_meal_confirmaion(callback: CallbackQuery, state: FSMContext):        
    data = await state.get_data()
    meal_type = data['meal_type']
    products = data['meal_products']
    text = (f"Вы хотите добавить следующий приём пищи:\n\n"
        f"Тип: {meal_type}\n")
    for i in range(len(products)):
        text += f"Блюдо {i+1}:\n"
        text += f"- Название: {products[i][0]}\n"
        text += f"- Количество: {products[i][-1]}г\n\n"
    kb = confirmation_keyboard()
    await state.set_state(AddNewMeal.confirmation)
    await callback.message.answer(text, reply_markup=kb) 
    await callback.message.delete()


@food_router.callback_query(
    F.data.in_(["confirmation_yes", "confirmation_no"]),
    StateFilter(AddNewMeal.confirmation)
)
async def process_meal_confirmation(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    text = callback.message.text
    if callback.data == "confirmation_no":
        text += "\n\n❌"
        await callback.message.edit_text(text)
        await callback.message.answer("❌ Добавление отменено")
    else:
        data = await state.get_data()
        try:
            await create_meal(session, callback.from_user.id, data)
            text += "\n\n✅"
            await callback.message.edit_text(text)
            await callback.message.answer("✅ Приём пищи успешно добавлен!")
        except Exception as e:
            await callback.message.answer("Что-то пошло не так при добавлении приёма пищи в базу данных...")
    kb = start_keyboard()
    await callback.message.answer("Выберите действие:", reply_markup=kb)
    await state.clear()
    await callback.answer()


@food_router.callback_query(F.data == "stat")
async def day_stats(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    today_meals = await get_today_meals(session, callback.from_user.id)
    if not today_meals:
        await callback.message.answer("Сегодня вы не добавляли приёмы пищи!")
    else:
        calories, protein, fats, carbs, fiber = 0, 0, 0, 0, 0
        text = "📊 Ваша статистика за сегодня:\n\n"
        for meal in today_meals:
            text += f"⏱️ {meal['time']} - <b>{meal['type'].title()}</b>\n"
            for product in meal['products']:
                text += f"・{product['name']}: {product['quantity']}г\n"
                calories += product['calories'] * product['quantity'] / 100
                protein += product['protein'] * product['quantity'] / 100
                fats += product['fats'] * product['quantity'] / 100
                carbs += product['carbs'] * product['quantity'] / 100
                fiber += product['fiber'] * product['quantity'] / 100
            text += "\n"
        text += "\n"
        text += "<b>Итого:</b>\n"
        text += f"<b>♨️ Калории:</b> {calories}\n"
        text += f"<b>🥩 Белки:</b> {round(protein / 10, 2)}г\n"
        text += f"<b>🧈 Жиры:</b> {round(fats / 10, 2)}г\n"
        text += f"<b>🍚 Углеводы:</b> {round(carbs / 10, 2)}г\n"
        text += f"<b>🥬 Пищевые волокна:</b> {round(fiber / 10, 2)}г\n"

        kb = plot_keyboard()
        await callback.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=kb)
        await state.set_state(Stats.plot)
        await state.update_data(today_meals=today_meals)
    kb = start_keyboard()
    await callback.message.answer("Выберите опцию", reply_markup=kb)

    await callback.answer()


@food_router.callback_query(F.data == "plot")
async def day_stats_plot(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    today_meals = data["today_meals"]
    chart_buffer = await generate_nutrition_chart(today_meals)
    await callback.message.answer_photo(
                BufferedInputFile(chart_buffer.getvalue(), "nutrition.png"),
                caption="Ваша статистика за сегодняшний день"
            )
    await state.clear()
    await callback.message.edit_text(callback.message.text)
    await callback.answer()

