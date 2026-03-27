"""
OpenAI AI Service
─────────────────────────────────────────────────────────────────────
Provides intelligent, context-aware crowd recommendations using GPT.

Features:
  • Best travel time narrative (explains WHY a time is good)
  • Crowd pattern insights for a location
  • Smart route suggestion reasoning
  • Alert trigger explanations
"""

import logging
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("openai package not installed. AI features disabled.")


# ── Prompt Templates ──────────────────────────────────────────────────────────

BEST_TIME_PROMPT = """
You are CrowdSense AI, a Mumbai transit and crowd expert assistant.
A user wants to travel from {from_location} to {to_location}.

Current crowd forecast data:
- Best hour to travel: {best_hour_label}
- Expected crowd density at best time: {expected_density:.1f}% ({status})
- 24-hour pattern summary: {pattern_summary}

Write a short, friendly, actionable recommendation (2-3 sentences max) explaining:
1. Why {best_hour_label} is the best time
2. What to expect at {from_location} and {to_location}
3. Any practical tip specific to Mumbai transit

Keep it conversational, helpful, and under 80 words.
""".strip()

CROWD_INSIGHT_PROMPT = """
You are CrowdSense AI, a Mumbai crowd prediction assistant.
Generate a brief insight about crowd patterns at {location_name} ({location_type}) in Mumbai.

Current stats:
- Current density: {current_density:.1f}% ({status})
- Time: {time_label}
- Is weekend: {is_weekend}

Write 1-2 sentences of insight about what to expect and any practical tip.
Keep it under 50 words. Be specific to Mumbai context.
""".strip()

ROUTE_SUGGESTION_PROMPT = """
You are CrowdSense AI helping a Mumbai commuter choose between locations.
The user wants to go to {destination} but it's too crowded ({destination_density:.1f}%).

Alternative options sorted by crowd density:
{alternatives_text}

Suggest which alternative is best and why, in 1-2 sentences. 
Mention approximate crowd difference. Under 60 words.
""".strip()

ALERT_EXPLANATION_PROMPT = """
CrowdSense AI alert triggered:
- Location: {location_name}
- Crowd density dropped to {density:.1f}% (below user threshold of {threshold:.1f}%)
- Time: {time_label}

Write a 1-sentence friendly alert message telling the user it's a good time to go.
Under 25 words. Be encouraging and specific.
""".strip()


class AIService:
    """Wraps OpenAI calls with fallbacks for when API is unavailable."""

    def __init__(self, api_key: str = "", model: str = "gpt-4o-mini"):
        self.model = model
        self.enabled = False
        self.client = None

        if api_key and OPENAI_AVAILABLE:
            try:
                self.client = AsyncOpenAI(api_key=api_key)
                self.enabled = True
                logger.info(f"OpenAI client initialized (model: {model})")
            except Exception as e:
                logger.error(f"Failed to init OpenAI: {e}")

    async def _call(self, prompt: str, max_tokens: int = 150) -> Optional[str]:
        """Make a single GPT call. Returns None on error."""
        if not self.enabled or not self.client:
            return None
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are CrowdSense AI, a helpful Mumbai transit and crowd "
                            "prediction assistant. Be concise, practical, and friendly."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI call failed: {e}")
            return None

    # ── Best Time Recommendation ───────────────────────────────────────────────

    async def get_best_time_recommendation(
        self,
        from_location: str,
        to_location: str,
        best_hour: int,
        expected_density: float,
        status: str,
        hourly_densities: List[tuple],  # [(hour, density), ...]
    ) -> str:
        """Returns an AI-generated travel recommendation string."""

        # Build pattern summary for prompt
        low_hours = [h for h, d in hourly_densities if d < 40]
        high_hours = [h for h, d in hourly_densities if d >= 70]

        def fmt_hour(h: int) -> str:
            if h == 0:
                return "midnight"
            elif h < 12:
                return f"{h} AM"
            elif h == 12:
                return "noon"
            else:
                return f"{h-12} PM"

        pattern_summary = (
            f"Low crowd hours: {', '.join(fmt_hour(h) for h in low_hours[:4])}. "
            f"Peak hours: {', '.join(fmt_hour(h) for h in high_hours[:4])}."
        )

        prompt = BEST_TIME_PROMPT.format(
            from_location=from_location,
            to_location=to_location,
            best_hour_label=fmt_hour(best_hour),
            expected_density=expected_density,
            status=status,
            pattern_summary=pattern_summary,
        )

        result = await self._call(prompt, max_tokens=120)
        if result:
            return result

        # Fallback: rule-based recommendation
        return self._fallback_best_time(
            from_location, to_location, best_hour, expected_density, status
        )

    def _fallback_best_time(
        self,
        from_location: str,
        to_location: str,
        best_hour: int,
        expected_density: float,
        status: str,
    ) -> str:
        def fmt(h):
            if h == 0: return "midnight"
            if h < 12: return f"{h} AM"
            if h == 12: return "12 PM"
            return f"{h-12} PM"

        tips = {
            "low": f"Great time to travel! Expect a comfortable journey with {expected_density:.0f}% crowd density.",
            "medium": f"Manageable crowds at {expected_density:.0f}%. Consider leaving a few minutes early.",
            "high": f"Crowds are at {expected_density:.0f}%. Try to travel with extra buffer time.",
        }
        tip = tips.get(status, tips["medium"])
        return (
            f"Best time to travel from {from_location} to {to_location} is around {fmt(best_hour)}. "
            f"{tip}"
        )

    # ── Location Crowd Insight ─────────────────────────────────────────────────

    async def get_crowd_insight(
        self,
        location_name: str,
        location_type: str,
        current_density: float,
        status: str,
        hour: int,
        is_weekend: bool,
    ) -> str:
        def fmt(h):
            if h < 12: return f"{h} AM"
            if h == 12: return "noon"
            return f"{h-12} PM"

        prompt = CROWD_INSIGHT_PROMPT.format(
            location_name=location_name,
            location_type=location_type,
            current_density=current_density,
            status=status,
            time_label=fmt(hour),
            is_weekend="Yes" if is_weekend else "No",
        )
        result = await self._call(prompt, max_tokens=80)
        return result or self._fallback_insight(location_name, current_density, status)

    def _fallback_insight(self, location_name: str, density: float, status: str) -> str:
        msgs = {
            "low": f"{location_name} is quiet right now at {density:.0f}%. Great time to visit!",
            "medium": f"Moderate activity at {location_name} ({density:.0f}%). Expect some wait times.",
            "high": f"{location_name} is busy at {density:.0f}%. Consider an alternative time.",
        }
        return msgs.get(status, msgs["medium"])

    # ── Smart Route Suggestion ─────────────────────────────────────────────────

    async def get_route_suggestion(
        self,
        destination: str,
        destination_density: float,
        alternatives: List[dict],  # [{name, density, status}, ...]
    ) -> str:
        if not alternatives:
            return f"{destination} is crowded. No similar alternatives found nearby."

        alts_text = "\n".join(
            f"- {a['name']}: {a['density']:.0f}% crowd ({a['status']})"
            for a in alternatives[:3]
        )

        prompt = ROUTE_SUGGESTION_PROMPT.format(
            destination=destination,
            destination_density=destination_density,
            alternatives_text=alts_text,
        )
        result = await self._call(prompt, max_tokens=100)
        best = alternatives[0]
        return result or (
            f"Try {best['name']} instead — it's much quieter at {best['density']:.0f}% "
            f"vs {destination_density:.0f}% at your original destination."
        )

    # ── Alert Message ──────────────────────────────────────────────────────────

    async def get_alert_message(
        self,
        location_name: str,
        density: float,
        threshold: float,
        hour: int,
    ) -> str:
        def fmt(h):
            if h < 12: return f"{h} AM"
            if h == 12: return "noon"
            return f"{h-12} PM"

        prompt = ALERT_EXPLANATION_PROMPT.format(
            location_name=location_name,
            density=density,
            threshold=threshold,
            time_label=fmt(hour),
        )
        result = await self._call(prompt, max_tokens=50)
        return result or (
            f"✅ {location_name} crowd dropped to {density:.0f}%! Good time to head out."
        )


# ── Singleton ─────────────────────────────────────────────────────────────────
ai_service: Optional[AIService] = None


def init_ai_service(api_key: str, model: str) -> AIService:
    global ai_service
    ai_service = AIService(api_key=api_key, model=model)
    return ai_service
