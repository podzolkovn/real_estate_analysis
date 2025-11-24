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
from app.infrastructure.db.repositories.inflation import InflationModelRepository
from app.infrastructure.db.repositories.nds import NDSModelRepository
from app.infrastructure.krisha_analitic import fetch_krisha_data


class ParserService:
    def __init__(
        self,
        build_analis_repo: Annotated[BuildingAnalisationModelRepository, Depends()],
        currency_rate_repo: Annotated[CurrencyRateModelRepository, Depends()],
        building_forecast_repo: Annotated[BuildingForecastModelRepository, Depends()],
        inflation_repo: Annotated[InflationModelRepository, Depends()],
        nds_repo: Annotated[NDSModelRepository, Depends()],

    ):
        self.build_analis_repo = build_analis_repo
        self.currency_rate_repo = currency_rate_repo
        self.building_forecast_repo = building_forecast_repo
        self.inflation_repo = inflation_repo
        self.nds_repo = nds_repo

    async def fetch_data_from_krisha(self):
        result: list[dict] = await fetch_krisha_data()
        logger.info(len(result))
        await self.build_analis_repo.upsert_many(result)

    async def predict_data(self):
        # 1. Получаем исторические данные
        buildings = await self.build_analis_repo.get_all()
        currency_rates = await self.currency_rate_repo.get_all()
        inflation = await self.inflation_repo.get_all()
        nds = await self.nds_repo.get_all()

        # 2. Формируем DataFrame
        building_df = pd.DataFrame([{
            "geo": b.geo,
            "geo_title": b.geo_title,
            "last_updated": pd.to_datetime(b.last_updated),
            "average": b.average
        } for b in buildings])

        currency_df = pd.DataFrame([{
            "date": pd.to_datetime(c.date),
            "usd": float(c.usd)
        } for c in currency_rates])

        inflation_df = pd.DataFrame([{
            "year": int(i.year),
            "inflation_rate": float(i.percent)
        } for i in inflation])

        nds_df = pd.DataFrame([{
            "year": int(n.year),
            "nds_rate": float(n.percent)
        } for n in nds])

        # 3. Добавляем год/месяц
        building_df["year"] = building_df["last_updated"].dt.year
        building_df["month"] = building_df["last_updated"].dt.month

        currency_df["year"] = currency_df["date"].dt.year
        currency_df["month"] = currency_df["date"].dt.month

        # -----------------------------
        # 4. ДОБАВЛЯЕМ ПРОГНОЗ ПРАВИТЕЛЬСТВА
        # -----------------------------
        future_inflation = pd.DataFrame([
            {"year": 2026, "inflation_rate": 0.10},  # среднее между 9–11%
            {"year": 2027, "inflation_rate": 0.06},
            {"year": 2028, "inflation_rate": 0.06},
        ])
        inflation_df = pd.concat([inflation_df, future_inflation]).drop_duplicates("year").reset_index(drop=True)

        future_currency = pd.DataFrame([
            {"date": pd.Timestamp("2026-01-01"), "usd": 548.2, "year": 2026, "month": 1},
            {"date": pd.Timestamp("2027-01-01"), "usd": 565.0, "year": 2027, "month": 1},
        ])
        currency_df = pd.concat([currency_df, future_currency]).drop_duplicates(["year", "month"]).reset_index(
            drop=True)

        # подготовим годовые маппинги для заполнения пропусков
        inflation_year_map = inflation_df.set_index("year")["inflation_rate"].to_dict()
        currency_year_map = currency_df.groupby("year")["usd"].first().to_dict()  # первая доступная в году

        # -----------------------------
        # 5. Соединяем курс USD с ценами
        # -----------------------------
        building_df = building_df.merge(
            currency_df[["year", "month", "usd"]],
            on=["year", "month"],
            how="left"
        )

        # Заполним пропуски usd месячного уровня годовым значением, затем медианой
        building_df["usd"] = building_df.apply(
            lambda r: currency_year_map.get(r["year"], r.get("usd")), axis=1
        )
        if building_df["usd"].isna().any():
            median_usd = currency_df["usd"].median() if not currency_df["usd"].isna().all() else 1.0
            building_df["usd"] = building_df["usd"].fillna(median_usd)

        building_df["average_kzt"] = building_df["average"] * building_df["usd"]

        # -----------------------------
        # 6. Соединяем инфляцию и НДС
        # -----------------------------
        building_df = building_df.merge(inflation_df, on="year", how="left")
        # если после merge есть NaN в inflation_rate, попробуем заполнить из годового маппинга
        building_df["inflation_rate"] = building_df.apply(
            lambda r: inflation_year_map.get(r["year"], r.get("inflation_rate")), axis=1
        )

        # дефолт если всё ещё NaN
        if building_df["inflation_rate"].isna().any():
            median_infl = inflation_df["inflation_rate"].median() if not inflation_df[
                "inflation_rate"].isna().all() else 0.0
            building_df["inflation_rate"] = building_df["inflation_rate"].fillna(median_infl)

        # nds
        building_df = building_df.merge(nds_df, on="year", how="left")
        building_df["nds_factor"] = 1.0
        # если у вас в nds_df есть проценты — применим к фактору
        if "nds_rate" in building_df.columns:
            building_df["nds_factor"] = building_df["nds_rate"].apply(
                lambda x: 1.0 if pd.isna(x) else (1.0 + x / 100.0)
            )
        # принудительный шаг: с 2026 минимально 1.16
        building_df.loc[building_df["year"] >= 2026, "nds_factor"] = building_df.loc[
            building_df["year"] >= 2026, "nds_factor"].apply(
            lambda x: max(x, 1.16)
        )

        building_df = building_df.sort_values(["geo_title", "last_updated"]).reset_index(drop=True)

        # -----------------------------
        # 7. Разделение по городам
        # -----------------------------
        series_dict = {}
        geo_mapping = {}
        for geo, geo_title in building_df[['geo', 'geo_title']].drop_duplicates().values:
            df_geo = building_df[building_df['geo_title'] == geo_title][[
                "last_updated",
                "average_kzt",
                "inflation_rate",
                "nds_factor",
                "usd"
            ]].copy()
            series_dict[geo_title] = df_geo
            geo_mapping[geo_title] = geo

        forecasts_result = {}

        # -----------------------------
        # 8. Прогноз для каждого города
        # -----------------------------
        for geo_title, df in series_dict.items():

            # Защита: если мало точек — пропускаем
            if df.shape[0] < 6:
                logger.warning(f"Skipping {geo_title}: not enough historical points ({df.shape[0]})")
                continue

            prophet_df = df.rename(columns={
                "last_updated": "ds",
                "average_kzt": "y",
                "usd": "usd_rate"
            }).reset_index(drop=True)

            # Заполняем регрессоры в исторических данных (ffill/bfill/замена на 0/1)
            prophet_df["inflation_rate"] = (
                prophet_df["inflation_rate"]
                .ffill()
                .bfill()
            )
            prophet_df["inflation_rate"] = prophet_df["inflation_rate"].fillna(
                inflation_df["inflation_rate"].median()
                if not inflation_df["inflation_rate"].isna().all() else 0.0
            )

            prophet_df["usd_rate"] = (
                prophet_df["usd_rate"]
                .ffill()
                .bfill()
            )
            prophet_df["usd_rate"] = prophet_df["usd_rate"].fillna(
                currency_df["usd"].median()
                if not currency_df["usd"].isna().all() else 1.0
            )

            prophet_df["nds_factor"] = (
                prophet_df["nds_factor"]
                .ffill()
                .bfill()
            )
            prophet_df["nds_factor"] = prophet_df["nds_factor"].apply(lambda x: max(x, 1.0))

            # ещё раз убеждаемся, что нет NaN
            if prophet_df[["inflation_rate", "usd_rate", "nds_factor"]].isna().any().any():
                logger.error(f"NaNs still present in regressors for {geo_title} before fit; skipping")
                continue

            model = Prophet(yearly_seasonality=True)
            model.add_regressor("inflation_rate")
            model.add_regressor("nds_factor")
            model.add_regressor("usd_rate")

            model.fit(prophet_df)

            # Future frame
            future = model.make_future_dataframe(periods=60, freq="ME")
            future["year"] = future["ds"].dt.year
            future["month"] = future["ds"].dt.month

            # добавляем прогноз инфляции (по году)
            future["inflation_rate"] = future["year"].map(inflation_year_map)
            # если NaN — заполнить медианой
            future["inflation_rate"] = future["inflation_rate"].fillna(
                inflation_df["inflation_rate"].median() if not inflation_df["inflation_rate"].isna().all() else 0.0)

            # добавляем прогноз usd (по месяцу/году), сначала по month/year, затем по yearly map, затем медианой
            future = future.merge(currency_df[["year", "month", "usd"]].rename(columns={"usd": "usd_rate"}),
                                  on=["year", "month"], how="left")
            future["usd_rate"] = future.apply(
                lambda r: r["usd_rate"] if not pd.isna(r["usd_rate"]) else currency_year_map.get(r["year"]), axis=1)
            future["usd_rate"] = future["usd_rate"].fillna(
                currency_df["usd"].median() if not currency_df["usd"].isna().all() else 1.0)

            # nds factor for future
            future["nds_factor"] = 1.0
            # если есть информация в nds_df по годам, использовать её
            nds_year_map = nds_df.set_index("year")["nds_rate"].to_dict() if not nds_df.empty else {}
            future["nds_factor"] = future["year"].map(
                lambda y: (1.0 + nds_year_map[y] / 100.0) if y in nds_year_map else 1.0)
            future.loc[future["year"] >= 2026, "nds_factor"] = future.loc[future["year"] >= 2026, "nds_factor"].apply(
                lambda x: max(x, 1.16))

            # Финальная проверка на NaN в регрессорах
            for col in ("inflation_rate", "usd_rate", "nds_factor"):
                if future[col].isna().any():
                    # последний резервный план: заполнить дефолтами
                    if col == "inflation_rate":
                        future[col] = future[col].fillna(inflation_df["inflation_rate"].median() if not inflation_df[
                            "inflation_rate"].isna().all() else 0.0)
                    elif col == "usd_rate":
                        future[col] = future[col].fillna(
                            currency_df["usd"].median() if not currency_df["usd"].isna().all() else 1.0)
                    else:
                        future[col] = future[col].fillna(1.0)

            # Предсказание
            forecast = model.predict(future)

            historical_last_date = df["last_updated"].max()
            forecast = forecast[forecast["ds"] > historical_last_date]

            # Сохранение
            forecast_rows = []
            for _, row in forecast.iterrows():
                forecast_rows.append(BuildingForecastModel(
                    geo=geo_mapping[geo_title],
                    geo_title=geo_title,
                    forecast_date=row["ds"].date(),
                    forecast_kzt=Decimal(row["yhat"]),
                    lower_bound_kzt=Decimal(row["yhat_lower"]),
                    upper_bound_kzt=Decimal(row["yhat_upper"])
                ))

            await self.building_forecast_repo.bulk_save_forecasts(forecast_rows)

            forecasts_result[geo_title] = forecast[[
                "ds", "yhat", "yhat_lower", "yhat_upper"
            ]].to_dict(orient="records")

        return forecasts_result
