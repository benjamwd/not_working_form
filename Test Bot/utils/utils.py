import asyncio
import json
import logging
from typing import List

import aiohttp
import discord
from discord import app_commands

class DiscordHandler(logging.Handler):
    def __init__(self, webhook_url):
        super().__init__()
        self.webhook_url = webhook_url
        self.formatter = logging.Formatter('```bash\n[{asctime}] [{levelname:<8}] {name}: {message}```', '%Y-%m-%d %H:%M:%S', style='{')
        self.tasks: List[asyncio.Task] = []
        self.timeout = aiohttp.ClientTimeout(total=10)

    def emit(self, record):
        try:
            log_entry = self.format(record)
            data = {"content": log_entry}
            headers = {"Content-Type": "application/json"}
            task = asyncio.create_task(self.async_emit(data, headers))
            task.add_done_callback(lambda t: self.tasks.remove(t) if t in self.tasks else None)
            self.tasks.append(task)
        except Exception as e:
            logging.error(f"Error in emit: {e}")

    async def async_emit(self, data, headers):
        retry_attempts = 3
        for attempt in range(retry_attempts):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.post(self.webhook_url, data=json.dumps(data), headers=headers) as response:
                        if response.status >= 400:
                            if response.status != 429:  # Don't retry on non-rate-limit errors
                                return
                        else:
                            return

            except aiohttp.ClientError as e:
                if attempt == retry_attempts - 1:
                    logging.error(f"Failed to send Discord webhook after {retry_attempts} attempts: {e}")
                    return
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                logging.error(f"Unexpected error in async_emit: {e}")
                return

    def close(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.async_close())
        except Exception as e:
            logging.error(f"Error during handler close: {e}")
        finally:
            loop.close()

    async def async_close(self):
        if self.tasks:
            pending = [t for t in self.tasks if not t.done()]
            if pending:
                await asyncio.wait_for(asyncio.gather(*pending, return_exceptions=True), timeout=5.0)


async def autocomplete(
            interaction: discord.Interaction,
            current: str,
            choices: list
        ) -> List[app_commands.Choice[str]]:
            return [
                app_commands.Choice(name=choice, value=choice)
                for choice in choices if current.lower() in choice.lower()
            ]