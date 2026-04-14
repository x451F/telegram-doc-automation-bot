"""Finite-state machine definitions for document workflow dialogs."""

from aiogram.fsm.state import State, StatesGroup


class DocumentWorkflowStates(StatesGroup):
    """States for generic service agreement / completion certificate intake."""

    choosing_document_type = State()
    entering_contract_number = State()
    entering_contract_date = State()
    entering_work_item_count = State()
    choosing_work_item = State()
    entering_custom_work_item = State()
    entering_contract_total_amount = State()
    entering_net_amount = State()
    entering_certificate_number = State()
    entering_certificate_date = State()
    entering_amount_in_words = State()
    reviewing_payload = State()
