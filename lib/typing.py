from typing import (
    List, Literal
)
import numpy as np
from numpy.typing import NDArray

Board = NDArray
Strategy = Literal["FC", "MIN_CONFLICT", "AC-3"]
