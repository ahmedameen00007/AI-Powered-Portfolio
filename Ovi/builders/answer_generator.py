"""
builders/answer_generator.py

LLM Answer Generator backend for the OVI chatbot.
Synthesizes retrieved RAG chunks into natural, professional language.
Uses the Groq API (SDK-based) with streaming support.
"""

from __future__ import annotations

import os
from typing import Any, Iterator

from builders.serializer import serialize_content


class AnswerGenerator:
    """
    Interfaces with the Groq API to synthesize a natural-language response
    based on the provided retrieval context chunks.
    """

    def __init__(self, model_name: str = "openai/gpt-oss-120b") -> None:
        self.model_name = model_name
        self._client = None

    def _get_client(self) -> Any:
        """Loads and returns the Groq client, raising user-friendly errors if misconfigured."""
        if self._client is not None:
            return self._client

        try:
            from groq import Groq
        except ImportError as exc:
            raise ImportError(
                "The 'groq' package is not installed. Please install it with:\n"
                "  pip install groq"
            ) from exc

        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable is not set. "
                "Please add it to your .env file."
            )

        self._client = Groq(api_key=api_key)
        return self._client

    def generate(
        self,
        query: str,
        retrieved_chunks: list[dict[str, Any]],
        history: list[dict[str, str]] | None = None,
        stream: bool = True,
        language: str = "en",
        entity_counts: dict[str, int] | None = None,
    ) -> Iterator[str] | str:
        """
        Formulates the prompt, includes retrieved chunks, and queries Groq.
        Supports token-by-token streaming (returns Iterator[str]) or full response (returns str).

        Args:
            entity_counts: Optional mapping of entity_type -> total count in the
                           full knowledge base (from Retriever.get_entity_counts()).
                           When provided, injected into the system prompt so the model
                           knows if the retrieved chunks are a partial list and can
                           inform the user accordingly.
        """
        client = self._get_client()

        # Format context chunks
        context_parts = []
        retrieved_type_counts: dict[str, int] = {}
        for i, chunk in enumerate(retrieved_chunks):
            etype = chunk["entity_type"]
            retrieved_type_counts[etype] = retrieved_type_counts.get(etype, 0) + 1
            # Serialize the chunk content to its deterministic text representation
            serialized_text = serialize_content(etype, chunk["content"])
            context_parts.append(
                f"Chunk {i+1} (Source: {chunk['source_file']}, Type: {etype}):\n"
                f"{serialized_text}"
            )

        context_str = "\n\n---\n\n".join(context_parts) if context_parts else "No relevant information found."

        # Build a knowledge-base totals hint so the model can tell the user
        # when the retrieved context is only a partial list.
        totals_note_en = ""
        totals_note_ar = ""
        if entity_counts:
            # Types where partial listing matters to the user
            _LIST_TYPES = ("certification", "project", "experience", "achievement")
            partial_hints_en = []
            partial_hints_ar = []
            for etype in _LIST_TYPES:
                total = entity_counts.get(etype, 0)
                shown = retrieved_type_counts.get(etype, 0)
                if total > 0:
                    label_map_en = {
                        "certification": "certification",
                        "project": "project",
                        "experience": "experience",
                        "achievement": "achievement",
                    }
                    label_map_ar = {
                        "certification": "شهادة",
                        "project": "مشروع",
                        "experience": "خبرة",
                        "achievement": "انجاز",
                    }
                    label_en = label_map_en[etype]
                    label_ar = label_map_ar[etype]
                    partial_hints_en.append(
                        f"  - {label_en}: {total} total in knowledge base, {shown} retrieved in current context"
                    )
                    partial_hints_ar.append(
                        f"  - {label_ar}: {total} في قاعدة البيانات، {shown} في السياق الحالي"
                    )
            if partial_hints_en:
                totals_note_en = (
                    "\nKnowledge Base Item Counts (for completeness awareness):\n"
                    + "\n".join(partial_hints_en)
                    + "\n"
                )
                totals_note_ar = (
                    "\nإحصائيات قاعدة البيانات (لمعرفة اكتمال القايمة):\n"
                    + "\n".join(partial_hints_ar)
                    + "\n"
                )

        if language == "ar":
            system_prompt = (
                "انت اوفي، مساعد ذكاء اصطناعي بيمثل احمد امين (مهندس Generative AI من الزقازيق، الشرقية، مصر).\n"
                "شغلتك انك تجاوب على الاسئلة عن احمد بدقة ودفا واحترافية، بس بس من المعلومات الموجودة في السياق اللي هيتديلك.\n\n"
                "القواعد:\n"
                "1. اتكلم عن احمد بصيغة الغائب (هو / بتاعه / شغله / خبرته).\n"
                "2. جاوب على سؤال اليوزر مباشرة بناء على السياق المتاح.\n"
                "3. اكتب بالعامية المصرية الطبيعية والودية. متستخدمش فصحى رسمية جامدة.\n"
                "4. كن دقيق في الاملاء والنحو العربي. متعملش اخطاء لغوية.\n"
                "5. مهم جدا: لو المعلومة مش موجودة في السياق، قول انك مش عارف بدل ما تخترع حاجة. متضفش معلومات من دماغك.\n"
                "6. لو في لينكات في السياق (زي لينكات التحقق من الشهادات او المشاريع)، اضيفها في الاجابة كما هي بالضبط.\n"
                "7. ترتيب القوايم: لما تعرض شهادات، رتبهم من الاحدث للاقدم (حسب تاريخ الانتهاء). لما تعرض خبرات، رتبهم من الاحدث للاقدم (حسب تاريخ البدء). الاحدث يجي اول.\n"
                "8. لو السياق فيه بس جزء من عناصر فئة معينة (زي مش كل الشهادات)، وضح للمستخدم ان في المزيد وعرض عليه انك تجيب تفاصيل اكتر.\n"
                f"{totals_note_ar}\n"
                f"السياق:\n---\n{context_str}\n---"
            )
        else:
            system_prompt = (
                "You are Ovi, a highly professional AI chatbot assistant representing Ahmed Ameen (a Generative AI Engineer based in Zagazig, Sharkia, Egypt).\n"
                "Your job is to answer questions about Ahmed accurately, professionally, and warmly, using ONLY the retrieved context chunks provided below.\n\n"
                "Rules:\n"
                "1. Speak in the third person about Ahmed (use 'he', 'him', 'his').\n"
                "2. Answer the user's question directly based on the provided Context.\n"
                "3. Be professional, honest, and concise. Do not add fluff or assume details.\n"
                "4. IMPORTANT: If the answer cannot be found or reasonably inferred from the provided Context, politely refuse to answer or say you do not know. Do NOT invent facts or hallucinate details (such as phone numbers, email addresses, or work experiences not present in the context).\n"
                "5. If the context has relevant links (like verification URLs or project URLs), include them in your answer where appropriate. Make sure the URLs are clean and exactly as specified in the context.\n"
                "6. ORDERING: When listing certifications or courses, order them newest first (by completion_date, most recent at top). When listing experiences, order them newest first (by start_date, most recent at top). Always show the latest ones first.\n"
                "7. COMPLETENESS: If the retrieved context contains only a subset of items from a category, explicitly tell the user how many items exist in total and how many are shown. Offer to provide details on any specific item. Example: 'Ahmed has 13 certifications in total. Here are the most relevant ones — ask me about any specific certification for full details.'\n"
                f"{totals_note_en}\n"
                f"Context Chunks:\n---\n{context_str}\n---"
            )

        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": query})

        if stream:
            def generator() -> Iterator[str]:
                try:
                    completion = client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        temperature=0.3 if language == "ar" else 0.2,
                        stream=True,
                    )
                    for chunk in completion:
                        content = chunk.choices[0].delta.content
                        if content:
                            yield content
                except Exception as exc:
                    yield f"\n✗ Groq API Error: {exc}"
            return generator()
        else:
            try:
                completion = client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.3 if language == "ar" else 0.2,
                    stream=False,
                )
                return completion.choices[0].message.content or ""
            except Exception as exc:
                return f"✗ Groq API Error: {exc}"
