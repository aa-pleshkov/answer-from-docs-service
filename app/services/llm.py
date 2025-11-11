from openai import OpenAI
from pathlib import Path
from langchain_community.adapters.openai import convert_message_to_dict
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings
from app.core.utils import logger
import json

class LLM:
    """Генерация ответов на вопросу на основе OpenAI API."""

    def __init__(self) -> None:
        try:
            self.api_key = settings.LLM_API_KEY
            self.base_url = settings.LLM_API_BASE
            self.model_name = settings.LLM_MODEL
            logger.debug(f"Инициализация LLM с моделью {self.model_name}")

            prompt_path = Path(settings.PATH_TO_SYSTEM_PROMPT)
            self.system_prompt = prompt_path.read_text(encoding="utf-8")
            logger.debug(f"System prompt загружен из {prompt_path}")

            schema_path = Path(settings.PATH_TO_ANSWER_SCHEMA)
            schema_text = schema_path.read_text(encoding="utf-8")
            self.answer_schema = json.loads(schema_text)
            logger.debug(f"Answer schema загружена из {schema_path}")

            self._setup_client()
            logger.info("LLM успешно инициализирован")
        except Exception as e:
            logger.critical(f"Критическая ошибка при инициализации LLM: {type(e).__name__}: {str(e)}", exc_info=True)
            raise

    def _setup_client(self) -> None:
        """
        Инициализирует OpenAI клиент с настройками из конфигурации.
        """
        try:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            logger.debug(f"OpenAI клиент инициализирован с base_url: {self.base_url}")
        except Exception as e:
            logger.error(f"Ошибка инициализации OpenAI клиента: {type(e).__name__}: {str(e)}")
            raise RuntimeError(f"Не удалось инициализировать клиент: {e}") from e

    def prompt_builder(self, user_question: str, document_text: str) -> list[dict]:
        """ Формирование шаблона для запроса к LLM. """

        try:
            if not user_question or not user_question.strip():
                raise ValueError("user_prompt не может быть корректно сформирован")
            if not document_text or not str(document_text).strip():
                raise ValueError("user_prompt не может быть корректно сформирован")
            user_prompt = f"Вопрос: {user_question}\nТекст документа: {document_text}"

            prompt = ChatPromptTemplate.from_messages([
                ("system", "{system_prompt}"),
                ("user", "{user_prompt}"),
            ])

            lc_msgs = prompt.format_messages(system_prompt=self.system_prompt, user_prompt=user_prompt)

            messages = [convert_message_to_dict(m) for m in lc_msgs]

            return messages
        
        except ValueError as e:
            logger.error(f"Ошибка валидации при формировании промпта: {e}")
            raise RuntimeError(f"Не удалось сформировать шаблон для запроса к LLM: {e}") from e
        except Exception as e:
            logger.error(f"Ошибка при формировании промпта: {type(e).__name__}: {str(e)}")
            raise RuntimeError(f"Не удалось сформировать шаблон для запроса к LLM: {e}") from e
    
    def generate_response(self, messages: list[dict]) -> str:
        """ Генерирует ответ на вопрос на основе шаблона. """

        try:
            if not messages:
                raise ValueError("Список сообщений не может быть пустым")
            
            logger.info(f"Отправка запроса к LLM-модели {self.model_name}...")
            chat = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "Answer",
                        "schema":self.answer_schema,
                        "strict": True,
                    },
                },
            )

            if not chat.choices:
                raise RuntimeError("LLM вернул пустой список choices")
            
            if not chat.choices[0].message:
                raise RuntimeError("LLM вернул choice без message")
            
            content = chat.choices[0].message.content
            try:
                content = json.loads(content)
                llm_response = content.get("answer_text")
                if not llm_response:
                    raise RuntimeError("Ответ LLM не содержит ключ answer_text")
                return llm_response
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Не удалось извлечь ответ из JSON: {e}") from e

        except ValueError as e:
            logger.error(f"Ошибка валидации при запросе к LLM: {e}")
            raise RuntimeError(f"Запрос к LLM провалился: {e}") from e
        except RuntimeError as e:
            logger.error(f"Ошибка обработки ответа LLM: {e}")
            raise
        except Exception as e:
            logger.error(f"Ошибка при запросе к LLM: {type(e).__name__}: {str(e)}", exc_info=True)
            raise RuntimeError(f"Запрос к LLM провалился: {e}") from e