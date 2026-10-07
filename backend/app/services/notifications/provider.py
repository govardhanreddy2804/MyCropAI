from abc import ABC, abstractmethod

from app.models.notification import Notification


class NotificationProvider(ABC):
    @abstractmethod
    def send(
        self,
        notification: Notification,
    ) -> Notification:
        raise NotImplementedError
