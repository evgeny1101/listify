from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

delete_confirm = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да, удалить", callback_data="confirm_delete"),
            InlineKeyboardButton(text="Отмена", callback_data="cancel_delete")
        ]
    ]
)