import asyncio
from functools import partial
from deep_translator import GoogleTranslator

class TranslationError(Exception):
    pass

class AsyncDeepTranslator:
    def __init__(self, timeout=10):
        self.translator = GoogleTranslator(source='auto', target='en')
        self.timeout = timeout

    async def translate(self, text, source='auto', target='en'):
        if source != 'auto' or target != 'en':
            self.translator = GoogleTranslator(source=source, target=target)
        
        loop = asyncio.get_running_loop()
        translate_func = partial(self.translator.translate, text)
        try:
            result = await asyncio.wait_for(loop.run_in_executor(None, translate_func), timeout=self.timeout)
            return result
        except asyncio.TimeoutError:
            raise TranslationError(f"Translation timed out after {self.timeout} seconds")
        except Exception as e:
            raise TranslationError(f"Translation error: {str(e)}")

    async def translate_batch(self, texts, source='auto', target='en'):
        if source != 'auto' or target != 'en':
            self.translator = GoogleTranslator(source=source, target=target)
        
        loop = asyncio.get_running_loop()
        translate_func = partial(self.translator.translate_batch, texts)
        try:
            result = await asyncio.wait_for(loop.run_in_executor(None, translate_func), timeout=self.timeout)
            return result
        except asyncio.TimeoutError:
            raise TranslationError(f"Batch translation timed out after {self.timeout} seconds")
        except Exception as e:
            raise TranslationError(f"Batch translation error: {str(e)}")