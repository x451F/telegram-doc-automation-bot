"""Finite-state machine definitions for document workflow dialogs."""

from aiogram.fsm.state import State, StatesGroup


class DocumentWorkflowStates(StatesGroup):
    """Core states for collecting data and generating documents."""

    choosing_template = State()
    entering_contract_number = State()
    entering_contract_date = State()
    entering_certificate_number = State()
    entering_work_items = State()
    confirming_payload = State()
    generating_output = State()

