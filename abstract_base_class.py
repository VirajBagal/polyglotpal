from abc import ABC, abstractmethod

class ChatBuddy(ABC):

    @abstractmethod
    def create_prompt(self):
        pass

    @abstractmethod
    def create_human_message(self):
        pass

    @abstractmethod
    def get_response(self):
        pass

    @abstractmethod
    def generate_audio(self):
        pass

    @abstractmethod
    def reset(self):
        pass