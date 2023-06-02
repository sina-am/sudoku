from typing import (
    Dict,
    Literal,
    Set,
    Tuple
)
import numpy as np
from numpy.typing import NDArray

Board = NDArray[np.uint8]
Domain = Dict[Tuple[int, int], Set[int]]
Strategy = Literal["FC", "MIN_CONFLICT", "AC-3"]
