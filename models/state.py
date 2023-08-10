#!/usr/bin/python3
"""State class model"""

from models.base_model import BaseModel

class State(BaseModel):
    """Represent a state.

    Attributes:
        name (str): The name of the state.
    """

    name = ""