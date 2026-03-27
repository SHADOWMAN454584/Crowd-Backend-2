from __future__ import annotations

from typing import Any

try:
    from openai import AsyncOpenAI
except Exception:
    AsyncOpenAI = None

try:
    from app.core.config import settings
except Exception:
    settings = None


def _serialize_crowd_items(items: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for item in items:
        lines.append(
            f"- {item.get('locationName', 'Unknown')}: density={item.get('crowdDensity', 0)}, "
            f"count={item.get('crowdCount', 0)}, status={item.get('status', 'low')}, "
            f"nextHour={item.get('predictedNextHour', 0)}"
        )
    return "\n".join(lines)


def _fallback_insights(items: list[dict[str, Any]]) -> dict[str, Any]:
    if not items:
        return {
            "summary": "No crowd data is currently available. Try collecting realtime data or requesting predictions first.",
            "source": "fallback",
        }

    busiest = max(items, key=lambda item: float(item.get("crowdDensity", 0)))
    calmest = min(items, key=lambda item: float(item.get("crowdDensity", 0)))
    summary = (
        f"The busiest location is {busiest.get('locationName', 'Unknown')} with a crowd density of "
        f"{busiest.get('crowdDensity', 0)}. The calmest area is {calmest.get('locationName', 'Unknown')} "
        f"at {calmest.get('crowdDensity', 0)}. Consider visiting lower-density areas during the next hour "
        f"when possible."
    )
    return {"summary": summary, "source": "fallback"}


def _fallback_route_advice(items: list[dict[str, Any]], origin: str | None = None, destination: str | None = None) -> dict[str, Any]:
    if not items:
        return {
            "advice": "No crowd data is available, so choose major roads and avoid peak commuting hours if possible.",
            "source": "fallback",
        }

    best_option = min(items, key=lambda item: float(item.get("crowdDensity", 0)))
    target = destination or best_option.get("locationName", "your destination")
    advice = (
        f"For travel from {origin or 'your current location'} to {target}, the best low-crowd option right now "
        f"is around {best_option.get('locationName', 'Unknown')} with density {best_option.get('crowdDensity', 0)}. "
        f"If your schedule is flexible, aim for the next hour when densities may shift toward "
        f"{best_option.get('predictedNextHour', 0)}."
    )
    return {"advice": advice, "source": "fallback"}


async def generate_insights_summary(items: list[dict[str, Any]]) -> dict[str, Any]:
    api_key = getattr(settings, "OPENAI_API_KEY", None) if settings else None
    model = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini") if settings else "gpt-4o-mini"
    if not api_key or AsyncOpenAI is None:
        return _fallback_insights(items)

    try:
        client = AsyncOpenAI(api_key=api_key)
        prompt = (
            "Summarize this crowd data for a population density app in 2-3 concise sentences.\n"
            f"{_serialize_crowd_items(items)}"
        )
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant for a population density monitoring app. Provide concise, actionable insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        text = response.choices[0].message.content.strip()
        if not text:
            return _fallback_insights(items)
        return {"summary": text, "source": "openai"}
    except Exception:
        return _fallback_insights(items)


async def generate_route_advice(items: list[dict[str, Any]], origin: str | None = None, destination: str | None = None) -> dict[str, Any]:
    api_key = getattr(settings, "OPENAI_API_KEY", None) if settings else None
    model = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini") if settings else "gpt-4o-mini"
    if not api_key or AsyncOpenAI is None:
        return _fallback_route_advice(items, origin=origin, destination=destination)

    try:
        client = AsyncOpenAI(api_key=api_key)
        prompt = (
            "Provide concise route timing advice for a crowd-aware travel app.\n"
            f"Origin: {origin or 'unknown'}\n"
            f"Destination: {destination or 'unknown'}\n"
            "Crowd data:\n"
            f"{_serialize_crowd_items(items)}"
        )
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a route planning assistant. Analyze crowd data and provide practical travel timing advice to avoid congestion."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
            temperature=0.7
        )
        text = response.choices[0].message.content.strip()
        if not text:
            return _fallback_route_advice(items, origin=origin, destination=destination)
        return {"advice": text, "source": "openai"}
    except Exception:
        return _fallback_route_advice(items, origin=origin, destination=destination)


async def generate_insights(crowd_data: list[dict[str, Any]]) -> dict[str, Any]:
    """Wrapper for API compatibility - accepts crowd_data parameter."""
    return await generate_insights_summary(crowd_data)