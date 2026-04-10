from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="cancel_add")]
        ]
    )
