from decimal import Decimal
from typing import Annotated
import pandas as pd
from fastapi import Depends
from prophet import Prophet
from app.core import logger
from app.infrastructure.db.models import BuildingForecastModel
from app.infrastructure.db.repositories.building_analisation import BuildingAnalisationModelRepository
from app.infrastructure.db.repositories.building_forecast import BuildingForecastModelRepository
from app.infrastructure.db.repositories.currency_rate import CurrencyRateModelRepository
from app.infrastructure.krisha_analitic import fetch_krisha_data


class ParserService:
    def __init__(
        self,
        build_analis_repo: Annotated[BuildingAnalisationModelRepository, Depends()],
        currency_rate_repo: Annotated[CurrencyRateModelRepository, Depends()],
        building_forecast_repo: Annotated[BuildingForecastModelRepository, Depends()]
    ):
        self.build_analis_repo = build_analis_repo
        self.currency_rate_repo = currency_rate_repo
        self.building_forecast_repo = building_forecast_repo

    async def fetch_data_from_krisha(self):
        result: list[dict] = await fetch_krisha_data()
        logger.info(len(result))
        await self.build_analis_repo.upsert_many(result)

    async def predict_data(self):
        # 1. Получаем исторические данные
        buildings = await self.build_analis_repo.get_all()
        currency_rates = await self.currency_rate_repo.get_all()

        # 2. Преобразуем в DataFrame
        building_df = pd.DataFrame([{
            "geo": b.geo,
            "geo_title": b.geo_title,
            "last_updated": b.last_updated,
            "average": b.average
        } for b in buildings])

        currency_df = pd.DataFrame([{
            "date": c.date,
            "usd": float(c.usd)
        } for c in currency_rates])

        building_df['last_updated'] = pd.to_datetime(building_df['last_updated'])
        currency_df['date'] = pd.to_datetime(currency_df['date'])

        # 3. Соединяем и пересчитываем KZT
        building_df['last_updated'] = pd.to_datetime(building_df['last_updated'])
        currency_df['date'] = pd.to_datetime(currency_df['date'])

        # Добавляем столбцы с годом и месяцем
        building_df['year'] = building_df['last_updated'].dt.year
        building_df['month'] = building_df['last_updated'].dt.month

        currency_df['year'] = currency_df['date'].dt.year
        currency_df['month'] = currency_df['date'].dt.month

        # 3. Соединяем по году и месяцу
        building_df = building_df.merge(
            currency_df[['year', 'month', 'usd']],
            on=['year', 'month'],
            how='left'
        )

        # Пересчитываем цены в KZT
        building_df['average_kzt'] = building_df['average'] * building_df['usd']

        # Сортировка
        building_df = building_df.sort_values(['geo_title', 'last_updated'])

        # 4. Формируем временные ряды
        series_dict = {}
        geo_mapping = {}  # для сохранения geo по geo_title
        for geo, geo_title in building_df[['geo', 'geo_title']].drop_duplicates().values:
            df_geo = building_df[building_df['geo_title'] == geo_title][['last_updated', 'average_kzt']]
            df_geo = df_geo.set_index('last_updated')
            series_dict[geo_title] = df_geo
            geo_mapping[geo_title] = geo

        # 5. Прогнозируем и сохраняем
        forecasts_result = {}
        for geo_title, df in series_dict.items():
            prophet_df = df.reset_index().rename(columns={'last_updated': 'ds', 'average_kzt': 'y'})
            model = Prophet(yearly_seasonality=True)
            model.fit(prophet_df)

            future = model.make_future_dataframe(periods=60, freq='ME')  # 5 лет
            forecast = model.predict(future)

            forecast = forecast[forecast['ds'] > df.index.max()]

            forecast_rows = []
            for _, row in forecast.iterrows():
                forecast_rows.append(BuildingForecastModel(
                    geo=geo_mapping[geo_title],
                    geo_title=geo_title,
                    forecast_date=row['ds'].date(),
                    forecast_kzt=Decimal(row['yhat']),
                    lower_bound_kzt=Decimal(row['yhat_lower']),
                    upper_bound_kzt=Decimal(row['yhat_upper'])
                ))

            await self.building_forecast_repo.bulk_save_forecasts(forecast_rows)
            forecasts_result[geo_title] = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict(orient='records')

        return forecasts_result