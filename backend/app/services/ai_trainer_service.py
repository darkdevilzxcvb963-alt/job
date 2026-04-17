import json
import re
import httpx
import asyncio
import logging
import os
import time
from typing import List, Optional, Dict, Any, Union
from loguru import logger


class AITrainerService:
    """
    Service for AI-powered career training using Google Gemini API.
    Implements multi-key rotation and model-level fallback for high availability.
    """

    def __init__(self):
        # --- Gemini API keys (rotated on 429 / quota errors) ---
        self.api_keys: List[str] = []
        self._load_keys()

        # Models to try in order (highest free-tier quota first)
        # gemini-2.0-flash: 15 RPM, 1500 RPD (best free quota)
        # gemini-2.5-flash: 10 RPM, 500 RPD
        # gemini-2.5-pro:   5 RPM, 25 RPD  (lowest — last resort)
        self.fallback_models: List[str] = [
            "gemini-2.0-flash",
            "gemini-2.5-flash",
            "gemini-2.5-pro",
        ]
        self.current_key_index: int = 0
        self.current_model_index: int = 0

        # Only use v1beta — newer models + responseMimeType only work here
        self.api_version: str = "v1beta"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

        # Rate-limit cooldown tracker: {"key_hash:model": expiry_timestamp}
        self._rate_limit_cooldown: Dict[str, float] = {}

        # --- Hugging Face settings ---
        self.hf_qwen_key = os.getenv("HUGGINGFACE_API_KEY", "")
        self.hf_qwen_model = "Qwen/Qwen2.5-7B-Instruct"
        self.qwen_url = f"https://router.huggingface.co/hf-inference/models/{self.hf_qwen_model}/v1/chat/completions"

        # --- Reliability Paths ---
        self.kb_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "knowledge_base.json")
        # Use absolute path for cache to avoid CWD issues
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
        self.cache_path = os.path.join(self.cache_dir, "interview_cache_v2.json")
        
        self.kb = self._load_json(self.kb_path)
        self.cache = self._load_json(self.cache_path)

    def _load_json(self, path: str) -> Dict[str, Any]:
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load JSON from {path}: {e}")
        return {}

    def _save_cache_safe(self, key: str, data: Dict[str, Any]):
        try:
            if not os.path.exists(self.cache_dir):
                os.makedirs(self.cache_dir, exist_ok=True)
                
            self.cache[key] = data
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
            logger.info(f"✅ Cache persisted to {self.cache_path}")
        except Exception as e:
            logger.error(f"Failed to save cache at {self.cache_path}: {e}")
            # Try a local path if absolute fails
            try:
                with open("interview_cache.json", 'w', encoding='utf-8') as f:
                    json.dump(self.cache, f, indent=2)
            except: pass

    # ------------------------------------------------------------------
    # Key loading
    # ------------------------------------------------------------------
    def _load_keys(self):
        """Pull keys from environment / settings — accepts any number."""
        # Try settings first, then raw env variables
        try:
            from app.core.config import settings
            for attr in ["GEMINI_API_KEY", "GEMINI_API_KEY_2",
                         "GEMINI_API_KEY_3", "GEMINI_API_KEY_4",
                         "GEMINI_API_KEY_5"]:
                val = getattr(settings, attr, "") or os.getenv(attr, "")
                if val and val.strip() and val.strip() not in self.api_keys:
                    self.api_keys.append(val.strip())
        except Exception:
            pass

        # Direct env fallback
        for attr in ["GEMINI_API_KEY", "GEMINI_API_KEY_2",
                     "GEMINI_API_KEY_3", "GEMINI_API_KEY_4",
                     "GEMINI_API_KEY_5"]:
            val = os.getenv(attr, "")
            if val and val.strip() and val.strip() not in self.api_keys:
                self.api_keys.append(val.strip())

        if not self.api_keys:
            logger.warning("⚠️  No Gemini API keys found — will use mock payload.")

    # ------------------------------------------------------------------
    # JSON helpers
    # ------------------------------------------------------------------
    def _parse_raw_json(self, text: str) -> Dict[str, Any]:
        """
        Cleanup and parse JSON from LLM output.
        """
        if not text:
            return {}

        # 1) Strip markdown fences
        if "```" in text:
            match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
            if match:
                text = match.group(1).strip()
            else:
                text = re.sub(r"^```(?:json)?\s*", "", text).strip()

        # 2) Direct parse attempt
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.debug(f"Initial JSON parse failed: {e}")

        # 3) Attempt to rescue: remove trailing commas
        text_fixed = re.sub(r',\s*([\]}])', r'\1', text)
        try:
            return json.loads(text_fixed)
        except json.JSONDecodeError:
            pass

        # 4) Attempt to rescue: Extract first { ... } block
        match = re.search(r"(\{.*\})", text_fixed, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # 5) Extreme salvage: Close braces manually if truncated
        try:
            last_bracket_end = text_fixed.rfind('}')
            if last_bracket_end != -1:
                chopped = text_fixed[:last_bracket_end+1]
                # Try to count open braces/brackets and close them
                # But a simple '}]}' is often enough if it died in questions
                for attempt in [ "]}", "}]}", "}}", "}]}]}" ]:
                    try:
                        res = json.loads(chopped + attempt)
                        logger.warning(f"Salvaged truncated JSON using '{attempt}' suffix!")
                        return res
                    except:
                        continue
        except Exception:
            pass

        logger.warning(f"JSON Parsing completely failed. Raw snippet: {text[:200]}")
        return {}

    def _sanitize_training_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensures the data matches our schema requirements (e.g. options is always a list)."""
        if not data or not isinstance(data, dict):
            return data
            
        questions = data.get("questions", [])
        if isinstance(questions, list):
            for idx, q in enumerate(questions):
                if not isinstance(q, dict): continue
                # Add a unique ID for frontend tracking
                q["id"] = f"q_{idx}_{hash(q.get('question', '')) % 10000}"
                # Fix options being null or missing
                if q.get("options") is None:
                    q["options"] = []
                # Ensure correct_answer is a string
                if q.get("correct_answer") is None:
                    q["correct_answer"] = ""
                # Default type if missing
                if not q.get("quiz_type"):
                    q["quiz_type"] = "mcq" if q.get("options") else "long_answer"
        return data

    # ------------------------------------------------------------------
    # Hugging Face fallback call
    # ------------------------------------------------------------------
    async def _call_huggingface(self, prompt: str) -> str:
        """
        Fallback to Hugging Face Qwen API if Gemini hits limit.
        """
        logger.info("Calling Hugging Face API as fallback.")
        headers = {
            "Authorization": f"Bearer {self.hf_qwen_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.hf_qwen_model,
            "messages": [
                {"role": "system", "content": "You are a highly capable AI return purely JSON without any markdown formatting."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 6000,
            "temperature": 0.3
        }

        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    self.qwen_url, 
                    headers=headers, 
                    json=payload,
                    timeout=70.0
                )
                
                if res.status_code == 200:
                    data = res.json()
                    usage = data.get("usage", {})
                    spent = usage.get("total_tokens", "Unknown") 
                    logger.info(f"Hugging Face API call successful. Tokens spent: {spent}")
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"Hugging Face API Error: {res.status_code} - {res.text[:200]}")
                    return ""
        except Exception as e:
            logger.error(f"Network error calling Hugging Face: {e}")
            return ""

    # ------------------------------------------------------------------
    # OpenRouter fallback call
    # ------------------------------------------------------------------
    async def _call_openrouter(self, prompt: str) -> str:
        """
        Fallback to OpenRouter API (Access to hundreds of models like Llama, Claude, etc).
        """
        # Try to get openrouter key from settings or env
        openrouter_key = ""
        try:
            from app.core.config import settings
            openrouter_key = getattr(settings, "OPENROUTER_API_KEY", "") or os.getenv("OPENROUTER_API_KEY", "")
        except Exception:
            openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
            
        if not openrouter_key:
            return ""

        logger.info("Calling OpenRouter API as fallback.")
        headers = {
            "Authorization": f"Bearer {openrouter_key}",
            "HTTP-Referer": "http://localhost:5173", # Recommended by OpenRouter
            "X-Title": "TrainingDashboard", # Recommended by OpenRouter
            "Content-Type": "application/json"
        }
        payload = {
            "model": "meta-llama/llama-3.1-8b-instruct:free", # Updated free model
            "messages": [
                {"role": "system", "content": "You are a highly capable AI. Return purely JSON without any markdown formatting."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }

        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions", 
                    headers=headers, 
                    json=payload,
                    timeout=70.0
                )
                
                if res.status_code == 200:
                    data = res.json()
                    logger.info("OpenRouter API call successful.")
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"OpenRouter API Error: {res.status_code} - {res.text[:200]}")
                    return ""
        except Exception as e:
            logger.error(f"Network error calling OpenRouter: {e}")
            return ""

    # ------------------------------------------------------------------
    # Groq API Configuration (Fastest)
    # ------------------------------------------------------------------
    async def _call_groq(self, prompt: str) -> str:
        """
        Fastest fallback using Groq API (LLaMA models). 
        """
        groq_key = os.getenv("GROQ_API_KEY", "")
        if not groq_key:
            return ""

        logger.info("Calling Groq API for rapid inference.")
        headers = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }
        
        # We append a JSON strictly hint if missing
        local_prompt = prompt
        
        payload = {
            "model": "llama3-70b-8192", 
            "messages": [
                {"role": "system", "content": "You are a highly capable AI. Return purely JSON without any markdown formatting. NO PREFACE. NO APPENDICES."},
                {"role": "user", "content": local_prompt}
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }

        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                if res.status_code == 200:
                    data = res.json()
                    logger.info("Groq API call successful.")
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"Groq API Error: {res.status_code} - {res.text[:200]}")
                    return ""
        except Exception as e:
            logger.error(f"Network error calling Groq: {e}")
            return ""


    async def _call_ollama(self, prompt: str) -> str:
        """
        Local fallback to Ollama running on localhost.
        """
        try:
            from app.core.config import settings
            model = settings.OLLAMA_MODEL
            base_url = settings.OLLAMA_BASE_URL
        except Exception:
            model = os.getenv("OLLAMA_MODEL", "llama3.2")
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

        logger.info(f"Calling Local Ollama API ({model}).")
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(f"{base_url}/api/generate", json=payload, timeout=90.0)
                if res.status_code == 200:
                    data = res.json()
                    return data.get("response", "")
                else:
                    logger.error(f"Local Ollama error: {res.status_code} - {res.text[:200]}")
                    return ""
        except Exception as e:
            logger.error(f"Network error calling Ollama: {e}")
            return ""

    # ------------------------------------------------------------------
    # Gemini REST call with key rotation + model fallback
    # ------------------------------------------------------------------
    def _is_cooled_down(self, key: str, model: str) -> bool:
        """Check if a key+model combo is still in rate-limit cooldown."""
        cd_key = f"{key[:8]}:{model}"
        expiry = self._rate_limit_cooldown.get(cd_key, 0)
        return time.time() < expiry

    def _set_cooldown(self, key: str, model: str, seconds: int = 65):
        """Mark a key+model combo as rate-limited for N seconds."""
        cd_key = f"{key[:8]}:{model}"
        self._rate_limit_cooldown[cd_key] = time.time() + seconds

    async def _call_gemini(self, prompt: str, max_models: int = 0) -> str:
        """
        Try key × model combinations until we get a 200.
        If max_models > 0, only try that many models before returning empty.
        This allows callers to interleave Ollama fallback between Gemini retries.
        Returns the model's text output or empty string on failure.
        """
        if not self.api_keys:
            return ""

        total_keys = len(self.api_keys)
        total_models = len(self.fallback_models)
        models_to_try = max_models if max_models > 0 else total_models

        for m_offset in range(min(models_to_try, total_models)):
            model = self.fallback_models[
                (self.current_model_index + m_offset) % total_models
            ]
            base = f"https://generativelanguage.googleapis.com/{self.api_version}/models"
            all_keys_limited = True

            for k_offset in range(total_keys):
                key = self.api_keys[
                    (self.current_key_index + k_offset) % total_keys
                ]

                # Skip keys in cooldown (already rate-limited recently)
                if self._is_cooled_down(key, model):
                    logger.debug(f"⏭ Skipping cooled-down key #{k_offset} for {model}")
                    continue

                all_keys_limited = False
                url = f"{base}/{model}:generateContent?key={key}"

                gen_cfg: Dict[str, Any] = {
                    "temperature": 0.35,
                    "maxOutputTokens": 20000,
                    "responseMimeType": "application/json"
                }

                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": gen_cfg,
                }
                try:
                    async with httpx.AsyncClient(timeout=35.0) as client:
                        res = await client.post(url, json=payload)

                    if res.status_code == 200:
                        self.current_key_index = (
                            self.current_key_index + k_offset + 1
                        ) % total_keys
                        data = res.json()
                        
                        # Log Token Limitation / Usage!
                        usage = data.get("usageMetadata", {})
                        tokens_spent = usage.get("totalTokenCount", "Unknown")
                        logger.info(f"Gemini OK: model={model} | Tokens Spent: {tokens_spent}")
                        
                        return (
                            data.get("candidates", [{}])[0]
                            .get("content", {})
                            .get("parts", [{}])[0]
                            .get("text", "")
                        )

                    if res.status_code == 429:
                        self._set_cooldown(key, model, 65)  # 65s cooldown
                        logger.warning(
                            f"⚠️ RATE LIMITED: Key #{k_offset} | Model: {model} → 429. Cooldown 65s."
                        )
                        continue

                    if res.status_code in (503, 500):
                        logger.warning(
                            f"⚠️ SERVER ERROR: Model: {model} → {res.status_code}. Trying next..."
                        )
                        continue

                    if res.status_code == 400:
                        # responseMimeType might not be supported — retry without it
                        error_text = res.text[:300]
                        if "responseMimeType" in error_text:
                            logger.warning(f"400: responseMimeType unsupported for {model}, retrying without it...")
                            del gen_cfg["responseMimeType"]
                            payload["generationConfig"] = gen_cfg
                            async with httpx.AsyncClient(timeout=35.0) as client:
                                res2 = await client.post(url, json=payload)
                            if res2.status_code == 200:
                                data = res2.json()
                                usage = data.get("usageMetadata", {})
                                logger.info(f"Gemini OK (no-mime): model={model} | Tokens: {usage.get('totalTokenCount', '?')}")
                                return (
                                    data.get("candidates", [{}])[0]
                                    .get("content", {})
                                    .get("parts", [{}])[0]
                                    .get("text", "")
                                )
                        logger.error(f"Gemini 400 error: {error_text}")
                        continue

                    if res.status_code == 404:
                        logger.warning(f"404: Model {model} not found, skipping...")
                        break  # Skip to next model

                    logger.error(f"Gemini error {res.status_code}: {res.text[:200]}")
                    continue

                except Exception as e:
                    logger.error(f"Network error calling Gemini ({model}): {e}")
                    continue

            # Exhausted all keys for this model → next model
            self.current_model_index = (self.current_model_index + 1) % total_models
            if all_keys_limited:
                logger.info(f"⏭ All keys cooled down for {model}, skipping instantly.")
            else:
                logger.warning(f"Moving to next model (exhausted {model})…")

        logger.warning("All attempted Gemini models/keys exhausted.")
        return ""

    # ------------------------------------------------------------------
    # Main public method
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # JIT Question Generation (Granular)
    # ------------------------------------------------------------------
    async def generate_questions_for_topic(
        self,
        topic: str,
        job_role: str,
        quiz_type: str = "Mixed",
        count: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Generates exactly 'count' questions for a specific topic.
        This is the core of the JIT / micro-generation engine.
        """
        logger.info(f"JIT: Generating {count} questions for topic: {topic}")
        
        # Micro-prompt for speed and reliability
        prompt = f"""You are an Expert AI Interviewer. 
        Target Topic: {topic}
        Role: {job_role}
        Count: {count} questions
        
        Generate exactly {count} distinct interview questions for {topic}.
        Distribute them as: 
        - 6 Multiple Choice (mcq)
        - 5 Fill-in-the-Blank (fill_in_the_blank)
        - 4 Short/Long Answer (long_answer)
        
        Return ONLY valid JSON in this structure:
        {{
          "questions": [
            {{
              "type": "medium",
              "question": "...",
              "cat": "{topic}",
              "quiz_type": "mcq",
              "options": ["Option A", "Option B", "Option C", "Option D"],
              "correct_answer": "Option A",
              "explanation": "..."
            }}
          ]
        }}
        
        CRITICAL RULES:
        1. "options" MUST be a list of strings for MCQs, and an empty list [] for others. NEVER return null for options.
        
        CRITICAL TO INCREASE SPEED: 
        1. Keep explanations ultra-short: strictly under 7 words!
        2. Set 'cat' to exactly "{topic}".
        3. Do NOT use markdown. Return raw JSON.
        """
        
        # Try ultra-fast Groq First
        raw = await self._call_groq(prompt)
        
        # Try best Gemini model first (1 model only for speed)
        if not raw:
            raw = await self._call_gemini(prompt, max_models=1)
        # Ollama is LOCAL and fast — try before exhausting all remote APIs
        if not raw:
            raw = await self._call_ollama(prompt)
        # If local Ollama also fails, try remaining Gemini models
        if not raw:
            raw = await self._call_gemini(prompt)
        if not raw:
            raw = await self._call_openrouter(prompt)
        if not raw:
            raw = await self._call_huggingface(prompt)
            
        parsed = self._parse_raw_json(raw)
        parsed = self._sanitize_training_data({"questions": parsed.get("questions", [])})
        questions = parsed.get("questions", [])
        
        # Ensure quality and count
        if len(questions) < count:
            # Check KB
            kb_key = next((k for k in self.kb.keys() if k.lower() == topic.lower()), None)
            if kb_key:
                kb_qs = self.kb[kb_key]
                for kq in kb_qs:
                    if len(questions) >= count: break
                    if not any(q.get('question') == kq.get('question') for q in questions):
                        questions.append({**kq, "cat": topic})
            
            # Fill the rest with mock if still missing
            while len(questions) < count:
                q_type = "mcq" if len(questions) < 4 else ("fill_in_the_blank" if len(questions) < 7 else "long_answer")
                questions.append({
                    "type": "medium",
                    "question": f"Expert question on {topic} #{len(questions)+1}",
                    "cat": topic,
                    "quiz_type": q_type,
                    "options": ["A", "B", "C", "D"] if q_type == "mcq" else [],
                    "correct_answer": "A" if q_type == "mcq" else "Sample Answer",
                    "explanation": "Standard industry practice."
                })
        
        return questions[:count]

    # ------------------------------------------------------------------
    # Main public method
    # ------------------------------------------------------------------
    async def generate_training_plan(
        self,
        job_role: str,
        candidate_skills: Union[str, List[str]],
        job_skills: Union[str, List[str]],
        matched_skills: Union[str, List[str]],
        question: Optional[str] = None,
        answer: Optional[str] = None,
        roadmap_days: int = 14,
        quiz_type: str = "Mixed",
        generate_all_questions: bool = False,
        chat_turn: int = 0
    ) -> Dict[str, Any]:

        def fs(s):
            return ", ".join(s) if isinstance(s, list) else str(s)

        cand_skills_str = fs(candidate_skills)
        job_skills_str = fs(job_skills)
        matched_str = fs(matched_skills)
        
        # Determine missing skills
        all_job_skills = job_skills if isinstance(job_skills, list) else [job_skills]
        all_cand_skills = candidate_skills if isinstance(candidate_skills, list) else [candidate_skills]
        missing_list = list(set(all_job_skills) - set(all_cand_skills))
        
        missing_str = fs(missing_list[:6]) if missing_list else "General interview skills"
        topics_to_cover = missing_list[:6] if missing_list else ["General"]
        
        # If generate_all_questions is False, target top 2 skill gaps by default.
        # This provides a healthy initial question bank (30 questions).
        target_topics = topics_to_cover if generate_all_questions else topics_to_cover[:2]
        
        quiz_instruction = f"""
For the topic(s) ({fs(target_topics)}), you MUST generate exactly 15 distinct interview questions PER topic:
- 6 Multiple Choice Questions (options + correct_answer)
- 5 Fill-in-the-Blank Questions
- 4 Short/Long Answer Questions
Set the "cat" field of each question to its EXACT topic name.
**CRITICAL**: Keep explanations strictly under 7 words to maximize generation speed!
"""

        # ---- evaluation section (only when answer provided) ----
        eval_section = ""
        if question and answer:
            eval_section = f"""
## ANSWER EVALUATION
Question asked: {question}
Candidate answered: {answer}
Evaluate and fill the "answer_evaluation" object.
"""

        # ---- L1: Cache / KB Lookup ----
        # Key must include answer to allow dynamic turn-based progression
        cache_key = f"{job_role}_{missing_str}_{roadmap_days}_{generate_all_questions}_{answer[:50] if answer else 'init'}"
        if cache_key in self.cache:
            logger.info(f"🚀 Cache Hit: Returning stored plan for {cache_key}")
            return self.cache[cache_key]

        prompt = f"""
You are an advanced Career Intelligence Engine.

SYSTEM PURPOSE:
You are NOT a chatbot. You do NOT engage in casual conversation. You ONLY analyze user data and generate structured career outputs.

STRICT RULES:
- No greetings, no explanations unless required, no storytelling.
- No general advice, no repetition.
- No asking follow-up questions.
- Output must be structured and direct. Think like a career analysis system, not a human assistant.

INPUT CONTEXT:
User Profile Skills: {cand_skills_str}
User Profile Interest: {job_role}
User Latest Input: {answer if answer else 'Initialization'}

INTELLIGENCE MODE:
If input contains "latest", "trend", "2025", "2026": Use advanced reasoning and include modern tools/frameworks.
If input is weak or unclear: Still generate output using assumptions (DO NOT ask questions).

OUTPUT STRUCTURE (JSON ONLY):
Return a JSON object conforming to this exact structure:
{{
  "coach_comment": "Final answer addressing user input. Must incorporate Q&A answers if relevant. Exactly 3 direct sentences.",
  "is_profile_complete": true,
  "skill_analysis": {{
     "level": "Determined level",
     "missing_skills": ["Missing skills based on industry demand"],
     "strengths": ["Core and Supporting Skills"],
     "focus_areas": ["Tools/Technologies"]
  }},
  "skill_profile": [ {{"skill": "Skill Name", "confidence": "0-100%"}} ],
  "top_job_matches": [ {{"role": "Role Name", "match_score": "0-100%", "why": "Why it fits (1 line only)"}} ],
  "roadmap": [ {{"day": "1", "focus": "Topic", "task": "Learning/Practice/Project details"}} ],
  "tasks": [ {{"title": "Task Name", "difficulty": "Hard/Medium/Easy", "description": "Expected Outcome", "requirements": ["Practical requirement"]}} ],
  "questions": [ {{"question": "Short tech question", "cat": "{job_role}", "quiz_type": "long_answer"}} ],
  "next_question": null
}}

ROADMAP RULE: Generate exactly {roadmap_days} individual roadmap array items. One for EVERY SINGLE day. (Day 1, Day 2, up to Day {roadmap_days}). DO NOT group days.
Q&A RULE: Generate 5 short interview questions inside the 'questions' array.
NEXT_QUESTION RULE: Always set "next_question": null. Never ask follow-ups.

CRITICAL: Return ONLY raw JSON. No markdown fences. Ensure precision and utility.
"""

        # 1. Try ultra-fast Groq API first
        raw = await self._call_groq(prompt)

        # 2. Try best Gemini model first (1 model only for speed)
        if not raw:
            raw = await self._call_gemini(prompt, max_models=1)

        # 3. Ollama is LOCAL and fast — try before exhausting all remote APIs
        if not raw:
            raw = await self._call_ollama(prompt)

        # 4. If local Ollama also fails, try remaining Gemini models
        if not raw:
            raw = await self._call_gemini(prompt)

        if not raw:
            raw = await self._call_openrouter(prompt)

        if not raw:
            return self._build_mock_payload(job_role, missing_list, roadmap_days, chat_turn, answer)

        parsed = self._parse_raw_json(raw)
        parsed = self._sanitize_training_data(parsed)
        
        # Ensure all requested topics have questions (fallback logic)
        existing_questions = parsed.get("questions", [])
        final_questions = []
        
        for t in target_topics:
            topic_qs = [q for q in existing_questions if str(q.get("cat", "")).lower() == str(t).lower()]
            # Relaxed strict checking to prevent blocking the UI layout if AI provides 13 instead of 15
            final_questions.extend(topic_qs)
            
        parsed["questions"] = final_questions
        parsed["job_role"] = job_role

        # Save to Cache
        if parsed and "skill_analysis" in parsed:
            self.cache[cache_key] = parsed
            self._save_cache_safe(cache_key, parsed)

        return parsed


    # ------------------------------------------------------------------
    # Mock fallback payload
    # ------------------------------------------------------------------
    def _build_mock_payload(
        self,
        job_role: str,
        missing_skills: List[str],
        roadmap_days: int,
        chat_turn: int = 0,
        user_answer: Optional[str] = None
    ) -> Dict[str, Any]:
        top_skills = missing_skills[:6] if missing_skills else ["Strategic Architecture", "Performance Optimization", "Full-Stack Orchestration"]
        ans_lower = (user_answer or "").lower()
        
        # CORE DECISION LOGIC (MOCK)
        if "ctc" in ans_lower or "salary" in ans_lower or "lpa" in ans_lower:
            resp = f"Market benchmark for {job_role} currently ranges from 12L to 28L LPA based on proficiency in {top_skills[0]}. Your profile's focus on scalable impact positions you in the top 20% of technical candidates. Strategic positioning for the next negotiation cycle starts with verifying these core skills."
        elif "role" in ans_lower or "job" in ans_lower:
            resp = f"Primary best-fit roles identified as {job_role}, Senior Infrastructure Architect, and Lead Engineer. These targets match your current baseline of architecture and human efficiency. I have finalized your match intelligence below."
        elif "skill" in ans_lower:
            resp = f"Critical skill gaps identified in {', '.join(top_skills[:3])} relative to global {job_role} standards. Bridging these gaps will provide a projected 15% uplift in recruiter search relevancy. Your core strengths are verified and indexed below."
        else:
            resp = f"Intelligent career analysis complete for your current session. I have mapped your technical baseline against {job_role} market standards. Review the finalized roadmap and targeted assignments below."

        return {
            "skill_analysis": {
                "level": "Elite Architect Tier",
                "missing_skills": top_skills,
                "strengths": ["Strategic Design", "Scalable Systems"],
                "focus_areas": ["Enterprise Orchestration"]
            },
            "questions": [],
            "tasks": [
                {"title": "System Scalability Audit", "description": "Conduct a performance audit on your latest project.", "requirements": ["Define metrics", "Identify bottlenecks"], "expected_output": "Audit Report", "difficulty": "Hard"}
            ],
            "roadmap": [
                {
                    "day": str(d), 
                    "focus": top_skills[d % len(top_skills)], 
                    "task": [
                        f"Set up and configure a sandbox environment exclusively designed for testing {top_skills[d % len(top_skills)]} principles.",
                        f"Run a structural analysis of an open-source repository utilizing {top_skills[d % len(top_skills)]}.",
                        f"Implement a small-scale prototype focusing heavily on {top_skills[d % len(top_skills)]} architectural bounds.",
                        f"Refactor a legacy application module adopting modern {top_skills[d % len(top_skills)]} design standards.",
                        f"Deploy the initial microservice highlighting optimized {top_skills[d % len(top_skills)]} protocols."
                    ][d % 5]
                }
                for d in range(1, roadmap_days + 1)
            ],
            "answer_evaluation": {"score": 10, "feedback": "Direct and strategic alignment.", "correct": True},
            "is_profile_complete": True,
            "next_question": None,
            "coach_comment": resp,
            "job_role": job_role,
            "skill_profile": [{"skill": s, "confidence": "85%"} for s in top_skills],
            "top_job_matches": [
                {"role": job_role, "match_score": "92%", "why": "Exceptional alignment with strategic system design."},
                {"role": "Lead Architect", "match_score": "88%", "why": "High proficiency in architectural efficiency themes."}
            ]
        }
