from typing import ClassVar

from time_manager.settings import HOST, PORT, SCHEME


class Server:
    root: ClassVar[str] = f"{SCHEME}://{HOST}:{PORT}"
    port: ClassVar[str] = PORT
    host: ClassVar[str] = HOST
    scheme: ClassVar[str] = SCHEME
