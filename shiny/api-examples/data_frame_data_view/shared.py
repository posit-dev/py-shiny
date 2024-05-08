from pathlib import Path

import pandas as pd

app_dir = Path(__file__).parent
mtcars = pd.read_csv(app_dir / "mtcars.csv")
