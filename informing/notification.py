from abc import ABC, abstractmethod
from typing import Union, Optional

from informing.tasks import send_email, send_sms


class Notification(ABC):
    @abstractmethod
    def create_instance(self):
        pass

    def setup(self):
        instance: Union[Sms, Email] = self.create_instance()
        return instance


class Message(ABC):
    @abstractmethod
    def send(self, to: str, subject: Optional[str] = None, message: Optional[str] = None) -> None:
        pass


class Email(Message):
    def send(self,
             to: str,
             subject: Optional[str] = None,
             message: Optional[str] = None) -> None:
        send_email.delay(to, subject, message)


class Sms(Message):
    def send(self,
             to: str,
             subject: Optional[str] = None,
             message: Optional[str] = None) -> None:
        send_sms.delay(to, subject, message)


class EmailNotification(Notification):
    def create_instance(self):
        return Email()


class SMSNotification(Notification):
    def create_instance(self):
        return Sms()


class NotificationService:
    type_ = {
        "email": EmailNotification,
        "sms": SMSNotification
    }

    def __new__(cls, *args, **kwargs):
        type_ = kwargs.get("type_", None)
        if type_ not in cls.type_:
            raise ValueError(f"Invalid type: {type_}")
        notification: Union[SMSNotification, EmailNotification] = cls.type_[type_]()
        notification_instance: Union[Sms, Email] = notification.setup()
        return notification_instance


