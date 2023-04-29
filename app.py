from chatbuddy import ConversationBuddy
from basemodels import ChatConfig, TranslateConfig, GenWordsConfig
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from constants import requests, prompts
import soundfile as sf
import openai
import io

load_dotenv()
polyglot = ConversationBuddy(temperature=0.9)
app = FastAPI()


@app.post("/chat_with_ai_in_text")
def generate_text(chat: ChatConfig):
    template = "I am trying to learn {language} language. I want to practice a scenario where I converse with a {role} in {language} language. You have to act as a {role} speaking in {language}. Wait for me to start the conversation."
    if not polyglot.is_prompt_created:
        polyglot.create_prompt(chat, template)
    if not polyglot.is_message_relevant(chat):
        polyglot.latest_response = "Not valid input"
        polyglot.generate_audio()
        return FileResponse("speech.mp3")
    polyglot.create_human_message(chat)
    polyglot.get_response()
    polyglot.generate_audio()
    return FileResponse("speech.mp3")


@app.post("/send_audio")
async def send_audio(sound: UploadFile = File(...)):
    sound_bytes = await sound.read()
    sound_data, samplerate = sf.read(io.BytesIO(sound_bytes))
    sf.write(sound.filename, sound_data, samplerate)
    dummy_file = open(sound.filename, "rb")
    transcription = openai.Audio.transcribe("whisper-1", dummy_file, language=iso_code)
    return {"transcription": transcription.text}


@app.post("/set_language_for_transcription")
async def set_language(text: GenWordsConfig):
    global iso_code
    iso_code = requests.language_to_iso[text.language]
    return {"status": "Successful"}


@app.get("/reset")
async def reset():
    polyglot.reset()
    return {"status": "Successful"}


@app.get("/translate")
async def translate():
    polyglot.translate(use_latest=True)
    return {"status": "Successful", "translation": polyglot.translated_latest_response}


@app.post("/translation_points")
async def calculate_translation_points(translate_config: TranslateConfig):
    polyglot.translate(use_latest=False)
    translation_points = polyglot.calculate_translation_points(translate_config.human_translation)
    return {"status": "Successful", "points": translation_points, "translation": polyglot.translated_latest_response}


@app.post("/get_sentences")
async def get_sentences(translate_config: TranslateConfig):
    example_prompt = {
        requests.HINDI: prompts.HINDI_EXAMPLE,
        requests.GERMAN: prompts.GERMAN_EXAMPLE,
        requests.FRENCH: prompts.FRENCH_EXAMPLE,
        requests.SPANISH: prompts.SPANISH_EXAMPLE,
        requests.CHINESE: prompts.CHINESE_EXAMPLE,
        requests.ENGLISH: prompts.ENGLISH_EXAMPLE
        # requests.KANNADA: prompts.KANNADA_EXAMPLE,
        # requests.MARATHI: prompts.MARATHI_EXAMPLE
    }
    pre_template = """Write a paragraph of {num_sentences} {language} sentence(s) containing common everyday words. Keep each sentence less than 10 words. \n \n"""
    example = example_prompt[translate_config.language]
    post_template = """\n \n DO NOT give its translation. \n \n RESPONSE:"""
    template = pre_template + example + post_template
    polyglot.create_prompt(translate_config, template)
    polyglot.get_response(insert_in_memory=False)
    polyglot.generate_audio()
    polyglot.reset_memory()
    return FileResponse("speech.mp3")


@app.post("/text_to_audio")
async def text_to_audio(config: GenWordsConfig):
    polyglot.generate_audio(config.language)
    return FileResponse("speech.mp3")


@app.post("/generate_words")
async def generate_words(config: GenWordsConfig):
    template = """Generate 5 everyday common verbs or nouns or adjectives in {language} and their translation in {native_language} in the following format:
    1. Word1 = Translation1
    2. Word2 = Translation2
    """
    polyglot.create_prompt(config, template)
    polyglot.get_response(insert_in_memory=False)
    polyglot.reset_memory()
    all_words = polyglot.latest_response.split("\n")
    practice_language_words = [" ".join(each_word.split("=")[0].strip().split(" ")[1:]) for each_word in all_words]
    native_language_words = [each_word.split("=")[1].strip() for each_word in all_words]
    return {
        "status": "Successful",
        "practice_language_words": practice_language_words,
        "native_language_words": native_language_words,
    }
