from pathlib import Path


BASE_DIR: Path = Path(__file__).parent
MAIN_DOC_URL= 'https://docs.python.org/3/'
PEPS_URL= 'https://peps.python.org/'
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
