from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_delete_confirm_keyboard(index: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Да, удалить", callback_data=f"confirm_delete:{index}"
                ),
                InlineKeyboardButton(
                    text="Отмена", callback_data=f"cancel_delete:{index}"
                ),
            ]
        ]
    )
