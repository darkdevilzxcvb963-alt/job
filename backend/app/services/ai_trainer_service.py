import json
import re
import httpx
import asyncio
import logging
import os
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

        # Models to try in order (newest → highest quota first)
        self.fallback_models: List[str] = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-flash-latest",
            "gemini-2.5-pro",
        ]
        self.current_key_index: int = 0
        self.current_model_index: int = 0

        # Try v1beta first, then v1 if needed
        self.api_versions: List[str] = ["v1beta", "v1"]
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

        # --- Hugging Face settings ---
        self.hf_qwen_key = os.getenv("HUGGINGFACE_API_KEY", "")
        self.hf_qwen_model = "Qwen/Qwen2.5-7B-Instruct"
        self.qwen_url = f"https://router.huggingface.co/hf-inference/models/{self.hf_qwen_model}/v1/chat/completions"

        # --- Reliability Paths ---
        self.kb_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "knowledge_base.json")
        # Use absolute path for cache to avoid CWD issues
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
        self.cache_path = os.path.join(self.cache_dir, "interview_cache.json")
        
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
            "model": "meta-llama/llama-3-8b-instruct:free", # Fast free model context
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
    # Gemini REST call with key rotation + model fallback
    # ------------------------------------------------------------------
    async def _call_gemini(self, prompt: str) -> str:
        """
        Try every key × every model combination until we get a 200.
        Returns the model's text output or empty string on total failure.
        """
        if not self.api_keys:
            return ""

        total_keys = len(self.api_keys)
        total_models = len(self.fallback_models)
        total_versions = len(self.api_versions)

        for m_offset in range(total_models):
            model = self.fallback_models[
                (self.current_model_index + m_offset) % total_models
            ]
            for v_offset in range(total_versions):
                api_ver = self.api_versions[v_offset]
                base = f"https://generativelanguage.googleapis.com/{api_ver}/models"

                for k_offset in range(total_keys):
                    key = self.api_keys[
                        (self.current_key_index + k_offset) % total_keys
                    ]
                    url = f"{base}/{model}:generateContent?key={key}"

                    gen_cfg: Dict[str, Any] = {
                        "temperature": 0.30,
                        "maxOutputTokens": 15000,
                        "response_mime_type": "application/json"
                    }

                    payload = {
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": gen_cfg,
                    }
                    try:
                        async with httpx.AsyncClient(timeout=70.0) as client:
                            res = await client.post(url, json=payload)

                        if res.status_code == 200:
                            self.current_key_index = (
                                self.current_key_index + k_offset + 1
                            ) % total_keys
                            data = res.json()
                            
                            # Log Token Limitation / Usage!
                            usage = data.get("usageMetadata", {})
                            tokens_spent = usage.get("totalTokenCount", "Unknown")
                            logger.info(f"Gemini OK: model={model} ({api_ver}) | Tokens Spent This Request: {tokens_spent}")
                            
                            return (
                                data.get("candidates", [{}])[0]
                                .get("content", {})
                                .get("parts", [{}])[0]
                                .get("text", "")
                            )

                        if res.status_code in (429, 503, 500):
                            logger.warning(
                                f"Key #{k_offset} / {model} ({api_ver}) → {res.status_code}. Rotating key…"
                            )
                            continue

                        if res.status_code == 404:
                            # Model not available on this API version — skip to next version
                            logger.warning(f"404: {model} not on {api_ver}, trying next version…")
                            break

                        logger.error(
                            f"Gemini error {res.status_code}: {res.text[:200]}"
                        )
                        continue

                    except Exception as e:
                        logger.error(f"Network error calling Gemini ({model}): {e}")
                        continue

            # Exhausted all keys + versions for this model → next model
            self.current_model_index = (self.current_model_index + 1) % total_models
            logger.warning(f"Moving to next model (exhausted {model})…")

        logger.error("All Gemini models, versions, and keys exhausted — using mock.")
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
        generate_all_questions: bool = False
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
        cache_key = f"{job_role}_{missing_str}_{roadmap_days}_{generate_all_questions}"
        if cache_key in self.cache:
            logger.info(f"🚀 Cache Hit: Returning stored plan for {cache_key}")
            return self.cache[cache_key]

        prompt = f"""You are an expert AI Career Coach.

## CONTEXT
- Target Job Role: {job_role}
- Skill Gaps (focus): {missing_str}
- Roadmap Duration: {roadmap_days} days
{eval_section}

## TASK
Generate a comprehensive career training plan. 
{quiz_instruction}

Generate exactly 5 practical tasks targeting the skill gaps.
Generate exactly {roadmap_days} roadmap days.

## OUTPUT — Return ONLY valid JSON in this exact structure:
{{
  "skill_analysis": {{
    "level": "Intermediate",
    "missing_skills": ["skill1", "skill2"],
    "strengths": ["strength1"],
    "focus_areas": ["focus1"]
  }},
  "questions": [
    {{
      "type": "medium",
      "question": "...",
      "cat": "Topic Name",
      "quiz_type": "mcq",
      "options": ["A. 1", "B. 2", "C. 3", "D. 4"],
      "correct_answer": "A. 1",
      "explanation": "..."
    }}
  ],
  "tasks": [
    {{
      "title": "...",
      "description": "...",
      "requirements": ["req1"],
      "expected_output": "...",
      "difficulty": "Medium"
    }}
  ],
  "roadmap": [
    {{"day": 1, "focus": "...", "task": "..."}}
  ],
  "answer_evaluation": null
}}

CRITICAL RULES:
1. Return ONLY JSON.
2. questions array MUST have exactly {len(target_topics) * 15} items.
3. tasks array MUST have exactly 5 items.
4. roadmap array MUST have exactly {roadmap_days} items.
"""

        raw = await self._call_gemini(prompt)

        if not raw:
            raw = await self._call_openrouter(prompt)

        if not raw:
            raw = await self._call_huggingface(prompt)
        
        if not raw:
            return self._build_mock_payload(job_role, missing_list, roadmap_days)

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
    ) -> Dict[str, Any]:
        top_skills = missing_skills[:6] if missing_skills else ["Python", "System Design", "Algorithms"]

        questions = []
        topics = top_skills

        for topic in topics:
            # 1. MCQs
            questions.append({
                "type": "medium",
                "question": f"How does {topic} contribute to effective {job_role} workflows?",
                "cat": topic,
                "quiz_type": "mcq",
                "options": [
                    "It automates repetitive manual processes",
                    "It provides a framework for data consistency",
                    "It enhances collaboration across technical teams",
                    "All of the above"
                ],
                "correct_answer": "All of the above",
                "explanation": "Modern tools excel at multi-faceted workflow improvements."
            })
            questions.append({
                "type": "medium",
                "question": f"Which best describes the primary use-case for {topic}?",
                "cat": topic,
                "quiz_type": "mcq",
                "options": [
                    "Data visualization and reporting",
                    "Core technical implementation",
                    "API integration management",
                    "Security and compliance auditing"
                ],
                "correct_answer": "Core technical implementation",
                "explanation": "This topic focuses on core domain logic."
            })
            
            # 2. Fill in the blanks
            for i in range(2):
                questions.append({
                    "type": "medium",
                    "question": f"[Fill] The key principle behind {topic} implementation involves ___ coordination.",
                    "cat": topic,
                    "quiz_type": "fill_in_the_blank",
                    "options": [],
                    "correct_answer": "Standardized",
                    "explanation": "Consistency is key in technical implementations."
                })

            # 3. Long answers
            for i in range(2):
                questions.append({
                    "type": "hard",
                    "question": f"How would you explain the strategic value of {topic} to a non-technical stakeholder?",
                    "cat": topic,
                    "quiz_type": "long_answer",
                    "options": [],
                    "correct_answer": "Focus on ROI, scalability, and risk mitigation.",
                    "explanation": "Focus on ROI, scalability, and risk mitigation."
                })

        tasks = [
            {
                "title": f"Master {top_skills[0] if top_skills else 'Core Skills'}",
                "description": f"Build a project demonstrating {top_skills[0] if top_skills else 'key skills'} proficiency.",
                "requirements": ["Research the fundamentals", "Implement a working example", "Write a reflection report"],
                "expected_output": "A working miniproject with documentation",
                "difficulty": "Medium",
            },
            {
                "title": "Design a Scalable Architecture",
                "description": "Create a system design document for a real-world use case.",
                "requirements": ["Define components", "Justify technology choices", "Include a diagram"],
                "expected_output": "System design doc + architecture diagram",
                "difficulty": "Hard",
            },
            {
                "title": "Mock Interview Practice",
                "description": "Complete 3 timed mock interview sessions using the questions above.",
                "requirements": ["Record yourself", "Self-evaluate each answer", "Identify weak areas"],
                "expected_output": "Video recording + self-assessment notes",
                "difficulty": "Easy",
            },
            {
                "title": "Build a Portfolio Project",
                "description": f"Create an end-to-end project showcasing {job_role} skills.",
                "requirements": ["Apply at least 3 gap skills", "Deploy it publicly", "Document the README"],
                "expected_output": "Live deployed project with GitHub link",
                "difficulty": "Hard",
            },
            {
                "title": "Review & Optimize",
                "description": "Revisit all completed tasks and optimize for quality and performance.",
                "requirements": ["Code review", "Performance benchmarking", "Update documentation"],
                "expected_output": "Optimized codebase with benchmark results",
                "difficulty": "Medium",
            },
        ]

        roadmap = [
            {
                "day": i + 1,
                "task": (
                    f"Study {top_skills[i % len(top_skills)]} fundamentals"
                    if i < len(top_skills)
                    else f"Practice and deep-dive: {job_role} role preparation"
                ),
                "focus": top_skills[i % len(top_skills)] if top_skills else "General",
            }
            for i in range(roadmap_days)
        ]

        return {
            "skill_analysis": {
                "level": "Developing",
                "missing_skills": top_skills,
                "strengths": ["Communication", "Willingness to learn"],
                "focus_areas": [f"Deep dive into {s}" for s in top_skills],
            },
            "questions": questions,
            "tasks": tasks,
            "roadmap": roadmap,
            "answer_evaluation": None,
        }
