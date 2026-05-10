import json
import os

import anthropic
from fastapi import HTTPException

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are an expert resume writer and career coach with 15 years of experience tailoring resumes for ATS systems and human recruiters.

RULES:
- Never fabricate experience, skills, dates, employer names, job titles, degrees, or GPA that are not in the original resume.
- You MAY rephrase bullet points, reorder sections, strengthen action verbs, and add relevant keywords from the job description where they accurately reflect the candidate's actual experience.
- Use strong action verbs: achieved, designed, led, delivered, built, optimized, reduced, increased, launched, managed.
- Quantify accomplishments where the original text implies measurable results (e.g., "improved performance" → "improved performance by ~30%").
- Rewrite the summary to be 3-4 sentences directly targeting the role described in the job description.
- Reorder skills so that those matching the job description appear first.
- Output ONLY valid JSON — no prose, no markdown code fences, no explanation."""

USER_PROMPT_TEMPLATE = """Analyze the following resume and job description, then produce a tailored version.

<original_resume>
{resume_text}
</original_resume>

<job_description>
{job_description}
</job_description>

Return a JSON object with EXACTLY this structure (omit sections that have no basis in the original resume — use empty arrays, not null):

{{
  "contact": {{
    "name": "string",
    "email": "string or empty string",
    "phone": "string or empty string",
    "location": "string or empty string",
    "linkedin": "string or empty string",
    "github": "string or empty string"
  }},
  "summary": "string — 3 to 4 sentences tailored to the role",
  "experience": [
    {{
      "title": "string",
      "company": "string",
      "location": "string or empty string",
      "start_date": "string",
      "end_date": "string",
      "bullets": ["string", "string"]
    }}
  ],
  "education": [
    {{
      "degree": "string",
      "institution": "string",
      "graduation_year": "string",
      "gpa": "string or empty string",
      "honors": "string or empty string"
    }}
  ],
  "skills": {{
    "technical": ["string"],
    "soft": ["string"]
  }},
  "certifications": ["string"],
  "projects": [
    {{
      "name": "string",
      "description": "string",
      "technologies": ["string"]
    }}
  ]
}}"""


def _extract_json(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:])
        if "```" in text:
            text = text[: text.rindex("```")]
    return json.loads(text.strip())


def tailor_resume(resume_text: str, job_description: str) -> dict:
    user_prompt = USER_PROMPT_TEMPLATE.format(
        resume_text=resume_text,
        job_description=job_description,
    )

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = response.content[0].text
        return _extract_json(raw)

    except anthropic.APIConnectionError as e:
        raise HTTPException(503, detail="AI service is temporarily unavailable. Please try again.") from e
    except anthropic.RateLimitError as e:
        raise HTTPException(429, detail="Too many requests. Please wait a moment and try again.") from e
    except anthropic.APIStatusError as e:
        raise HTTPException(502, detail="AI service returned an error. Please try again.") from e
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(500, detail="Failed to parse AI response. Please try again.") from e
