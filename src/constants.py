from pathlib import Path


BASE_DIR: Path = Path(__file__).parent
MAIN_DOC_URL: str = 'https://docs.python.org/3/'
PEPS_URL: str = 'https://peps.python.org/'
DATETIME_FORMAT: str = '%Y-%m-%d_%H-%M-%S'
EXPECTED_STATUS: dict[str, tuple[str]] = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
