from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND


class NotFoundedError(HTTPException):
    def __init__(self) -> None:
        self.status_code = HTTP_404_NOT_FOUND
        self.detail = "Такой записи нет в базе данных"