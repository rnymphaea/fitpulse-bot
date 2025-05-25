from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter

from sqlalchemy.ext.asyncio import AsyncSession

from keyboards import food as kb_food
from keyboards.common import confirmation_keyboard
from storage.food import * # TODO: list functions

router = Router()

class AddNewProduct(StatesGroup):
    name = State()
    calories = State()
    pfc = State()
    fiber = State()
    confirmation = State()

@router.callback_query(F.data == "food")
async def food(callback: CallbackQuery):
    kb = kb_food.select_option_keyboard()
    await callback.message.edit_text("Выберите опцию", reply_markup=kb)

@router.callback_query(F.data == "add_plate")
async def add_product(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название блюда")
    await state.set_state(AddNewProduct.name)


@router.message(AddNewProduct.name)
async def process_product_name(message: Message, state: FSMContext, session: AsyncSession):
    telegram_id = message.from_user.id
    name = message.text
    exists = await product_exists(session, telegram_id, name.lower())
    if exists:
        await message.answer("Блюдо уже есть в вашем списке!")
    else:
        await message.answer("Введите количество калорий")
        await state.update_data(name=name)
        await state.set_state(AddNewProduct.calories)

@router.message(AddNewProduct.calories)
async def process_product_calories(message: Message, state: FSMContext):
    try:
        calories = int(message.text)
        await message.answer("Введите БЖУ на 100г блюда через пробел. \n Пример: 15.6 20.1 50.3")
        await state.update_data(calories=calories)
        await state.set_state(AddNewProduct.pfc)

    except ValueError:
        await message.answer("Неверный формат данных! Введите целое число.")
    

@router.message(AddNewProduct.pfc)
async def process_product_pfc(message: Message, state: FSMContext):
    try:
        protein, fats, carbs = map(lambda x: int(x * 10), map(float, message.text.split()))
        await message.answer("Введите содержание пищевых волокон, если указано.")
        await state.update_data(pfc=(protein, fats, carbs))
        await state.set_state(AddNewProduct.fiber)
    except ValueError:
        await message.answer("Неверный формат данных! \n Введите БЖУ на 100г блюда через пробел. \n Пример: 15.6 20.1 50.3")
        

@router.message(AddNewProduct.fiber)
async def process_product_fiber(message: Message, state: FSMContext):
    try:
        fiber = int(float(message.text) * 10)
        info = await state.get_data()
        name = info['name']
        calories = info['calories']
        protein, fats, carbs = info['pfc']
        
        answer_text = (f"Вы хотите добавить следующее блюдо:\n"
            f"Название: {name}\n"
            f"Калории: {calories}\n"
            f"Белки: {protein}г\n"
            f"Жиры: {fats}г\n"
            f"Углеводы: {carbs}г\n"
            f"Пищевые волокна: {fiber}\n?")
        kb = confirmation_keyboard()

        await message.answer(answer_text, reply_markup=kb)
        await state.update_data(fiber=fiber)
        await state.set_state(AddNewProduct.confirmation)
    except ValueError:
        await message.answer("Неверный формат данных! \n Введите целое число.")


@router.callback_query(
    F.data.in_(["confirmation_yes", "confirmation_no"]),
    StateFilter(AddNewProduct.confirmation)
)
async def process_confirmaion(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
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
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "meals")
async def food(callback: CallbackQuery):
    kb = kb_food.meals_keyboard()
    await callback.message.edit_text("Какой приём пищи вы хотите добавить?", reply_markup=kb)

@router.callback_query(F.data == "breakfast")
async def add_breakfast(callback: CallbackQuery):
    await callback.message.answer("Что вы ели на завтрак?")
