from pydantic import BaseModel

class ChatConfig(BaseModel):
    role: str
    language: str
    text: str
    native_language: str

class TranslateConfig(BaseModel):
    language: str
    native_language: str
    num_sentences: int
    human_translation: str

class GenWordsConfig(BaseModel):
    language: str
    native_language: str   