import httpx
from typing import Any, Dict, List

class CoinGeckoService:
    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self):
        self.headers = {
            "accept": "application/json",
        }

    async def _get(self, endpoint: str) -> Dict[str, Any]:
        """Generic GET request to CoinGecko API"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}{endpoint}", headers=self.headers)
            response.raise_for_status()
            return response.json()
        return None
    
    async def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("POST method not implemented")

    async def _put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("PUT method not implemented")

    async def _delete(self, endpoint: str) -> None:
        raise NotImplementedError("DELETE method not implemented")

    async def get_coins_by_symbol(self, symbol: str) -> List[Dict[str, Any]]:
        """Fetch coins by symbol"""
        coins = await self._get("/coins/list?include_platform=true")

        coins_ = []
        for coin in coins:
            if coin["symbol"].lower() == symbol.lower():
                coin_id = coin["id"]
                coin_platforms = tuple(coin.get("platforms", {}).keys())
                coins_.append({"id": coin_id, "platforms": coin_platforms})
        
        return coins_
    
    async def get_price(self, coin_id: str, currency: str) -> Dict[str, Any]:
        """Fetch price for a given coin and currency"""
        endpoint = f"/simple/price?ids={coin_id}&vs_currencies={currency}"
        return await self._get(endpoint)
