# Frontend (WeChat Mini Program)

## Run in WeChat DevTools

1. Open WeChat DevTools and choose `Import Project`.
2. Select `frontend` as project directory.
3. AppID can use test AppID for local development.
4. Keep backend running at `http://127.0.0.1:8000`.

## API Link

- Page: `pages/index/index`
- Button action: call `GET /api/v1/health`
- Request wrapper: `utils/request.js`
- Base URL config: `config/env.js`

## Notes

- Simulator uses `127.0.0.1:8000` by default.
- For real device debugging, change `LAN_BASE_URL` in `config/env.js` to your computer LAN IP.
- If request fails due to domain check, open DevTools settings and disable request domain verification for local debug.
