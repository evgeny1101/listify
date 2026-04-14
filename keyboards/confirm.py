from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def _cancel_button(target: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text="Отмена", callback_data=f"cancel:delete:{target}")


def get_delete_confirm_keyboard(index: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Да, удалить", callback_data=f"confirm:delete:{index}"
                ),
                _cancel_button(str(index)),
            ]
        ]
    )


def get_multi_delete_keyboard(ids: list[int]) -> InlineKeyboardMarkup:
    ids_str = ",".join(map(str, ids))
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Да, удалить все", callback_data=f"confirm:delete:{ids_str}"
                ),
                _cancel_button(ids_str),
            ]
        ]
    )
