import base64
import os

from cryptography.fernet import Fernet


class Encoder(object):
    __slots__ = (
        "__key", "file"
    )

    def __init__(self, key: bytes = None, save_key: bool = False) -> None:
        self.__key = Fernet.generate_key() if key is None else key
        if save_key:
            if not os.path.exists(".json"):
                os.mkdir(".json")
            with open(".json/key.dpcb", "+wb") as self.file:
                self.file.write(self.__key)

    def encrypt(self, text: str = None) -> bytes:
        return Fernet(self.__key).encrypt(self.__to_base64(text))

    def decrypt(self, text: bytes = None) -> str:
        return self.__from_base64(Fernet(self.__key).decrypt(text))

    @property
    def key(self) -> bytes:
        return self.__key

    @key.setter
    def key(self, value: str) -> None:
        self.__key = value.encode()

    @staticmethod
    def __to_base64(text: str) -> bytes:
        return base64.b64encode(bytes(text, 'utf-8'))

    @staticmethod
    def __from_base64(text: bytes) -> str:
        return base64.b64decode(text).decode()
