# Guardrails

`SmartHotelChatbot` is a domain-focused assistant for:
- hotel booking flow
- cancellation and modification
- hotel amenities and policy FAQ

## Behavior rules

1. Stay within hotel booking domain and related policy Q&A.
2. Refuse unsafe or illegal requests.
3. Refuse clearly out-of-scope requests (finance, medical, legal, etc.).
4. Keep responses short, polite, and redirect user to booking-related flow.
5. Remind users this is a demo and does not perform real payment.

## Current implementation

- Rule-based check in `backend/app/services/chat.py`:
  - `_is_unsafe_or_out_of_scope(message)`
  - returns `intent="guardrail"` with a safe redirect reply

## Planned improvements

- Externalize blocked keyword sets into config/env.
- Add language-specific guardrail templates (TR/EN).
- Add monitoring for guardrail trigger rate.
