# GeoLocator API

Простой API-сервер на Flask для определения координат по адресу и наоборот с помощью Google Maps Geocoding API.

## Запуск локально
```bash
pip install -r requirements.txt
python main.py
```

## Для деплоя на Railway
- Залей проект на GitHub
- В Railway выбери "Deploy from GitHub"
- Railway автоматически подтянет зависимости и запустит через `Procfile`

## URL endpoints
- `/get-coordinates?address=Кривой+Рог`
- `/get-location?lat=47.9&lon=33.4`
