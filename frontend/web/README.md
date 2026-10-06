# Interview interface

React + TypeScript + Vite frontend for Interview. Routes cover dashboard, setup, live room, sample reports, history, and settings. Most analytics/report values are examples; this is a development interface.

## Local use

```bash
npm ci
cp .env.example .env
npm run dev
```

Run from this directory. Use the URL printed by Vite. `npm run build` compiles to `dist`; `npm run preview` serves that build locally.

`VITE_API_URL` selects the HTTP origin; `VITE_WS_URL` selects the socket origin. Both are public build-time configuration. Never put provider keys here.

Text uses `/ws/interview`; microphone signaling uses `/webrtc/offer`. Voice has known backend defects. The frontend does not use `/ws/audio`. Fallback demo questions and static reports do not establish backend success.

See [setup](../../docs/getting_started.md), [API](../../docs/api.md), and [hosting](../../docs/deployment.md) for details. UI routes and behavior live in `src/App.tsx`; styling lives in `src/styles.css`.
