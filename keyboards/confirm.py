from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


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


def get_multi_delete_keyboard(ids: list[int]) -> InlineKeyboardMarkup:
    ids_str = ",".join(map(str, ids))
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Да, удалить все", callback_data=f"confirm_delete:{ids_str}"
                ),
                InlineKeyboardButton(
                    text="Отмена", callback_data=f"cancel_delete:{ids_str}"
                ),
            ]
        ]
    )
