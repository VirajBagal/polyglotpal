from abstract_base_class import ChatBuddy
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from text_to_speech import convert_text_to_audio

class ConversationBuddy(ChatBuddy):
    def __init__(self, temperature):
        self.model = ChatOpenAI(temperature=temperature, model = "gpt-4")
        self.is_prompt_created = False
        self.latest_response = ""
        self.second_last_response = ""
        self.translated_latest_response = ""
        self.config = None
        self.memory = []

    def create_prompt(self, chat_config, template):
        formatted_template = template.format(**vars(chat_config))
        system_message = SystemMessage(content = formatted_template)
        self.memory.append(system_message)
        self.config = chat_config
        self.is_prompt_created = True

    def is_message_relevant(self, chat_config):
        relevance_template = f"Is the following text relevant to a {chat_config.role}? Respond only 'Yes' or 'No': "
        relevance_message = relevance_template + chat_config.text
        relevance_message = HumanMessage(content = relevance_message)
        self.memory.append(relevance_message)
        self.get_response(insert_in_memory = False)
        self.memory.pop()
        if "Yes" in self.latest_response:
            return True
        return False

    def create_human_message(self, chat_config):
        human_message = HumanMessage(content = chat_config.text)
        self.memory.append(human_message)

    def get_response(self, insert_in_memory = True):
        response = self.model(self.memory)
        self.second_last_response = self.latest_response
        self.latest_response = response.content
        if insert_in_memory:
            self.memory.append(response)

    def generate_audio(self, text = None):
        if text:
            convert_text_to_audio(text)
        else:
            convert_text_to_audio(self.latest_response)

    def reset(self):
        self.is_prompt_created = False
        self.latest_response = ""
        self.translated_latest_response = ""
        self.reset_memory()

    def reset_memory(self):
        self.memory = []

    def translate(self, use_latest):
        text_to_be_translated = self.latest_response if use_latest else self.second_last_response
        if text_to_be_translated == "":
            self.translated_latest_response = ""
            return
        template = "Translate the following in {native_language}. Strictly only give the translated output and nothing else: '{latest_response}'"
        formatted_template = template.format(native_language = self.config.native_language, latest_response = text_to_be_translated)
        human_message = HumanMessage(content = formatted_template)
        self.translated_latest_response = self.model([human_message]).content

    def calculate_translation_points(self, text):
        if text == "":
            return 0
        template = f"""On a scale of 1 to 10, how much would you rate the following sentences on semantic similarity. Just give a number as output: 
        1. {self.translated_latest_response}
        2. {text}
        """
        human_message = HumanMessage(content = template)
        response = self.model([human_message])
        return int(float(response.content))


        

    
