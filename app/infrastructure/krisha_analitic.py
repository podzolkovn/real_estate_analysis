import httpx

URL = "https://krisha.kz/spa-api/content/analytics/sale?id=0&rooms&buildingType&mode=short"


async def fetch_krisha_data():
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
        response = await client.get(URL)
        response.raise_for_status()
        data = response.json()
        return data
