import httpx
from typing import Any, Dict, List
from app.cache import CacheService

class CoinGeckoService:
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self):
        self.headers = {
            "accept": "application/json",
        }
        self.cache = CacheService()

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

    async def get_all_coins_platforms(self) -> List[Dict[str, Any]]:
        """Fetch and cache the complete list of coins with platforms"""
        coins_list_cache_key = "coingecko:coins_platforms:all"
        cached_data = self.cache.get(coins_list_cache_key)
        if cached_data is not None:
            return cached_data
        
        # If not in cache, fetch from API
        coins = await self._get("/coins/list?include_platform=true")
        
        self.cache.set(coins_list_cache_key, coins)
        return coins

    async def get_coins_platforms(self, symbol: str) -> Dict[str, List[str]]:
        """Fetch coins and their platforms by symbol"""
        all_coins = await self.get_all_coins_platforms()

        coins_ = {}
        for coin in all_coins:
            if coin["symbol"].lower() == symbol.lower():
                coin_id = coin["id"]
                platforms_keys = list(coin.get("platforms", {}).keys())
                coin_platforms = platforms_keys if platforms_keys else [coin_id]
                coins_[coin_id] = coin_platforms
        
        return coins_
    
    async def get_coin_id(self, symbol: str, platform: str) -> str:
        """Fetch coin ID by symbol and platform"""
        coins = await self.get_coins_platforms(symbol)
        
        for coin_id, platforms in coins.items():
            if platform in platforms:
                return coin_id
        return None
    
    async def get_price(self, coin_id: str, currency: str) -> Dict[str, Any]:
        """Fetch price for a given coin and currency"""
        cache_key = f"coingecko:price:{coin_id}:{currency.lower()}"
        
        cached_price = self.cache.get(cache_key)
        
        try:
            # Try to get fresh price data from API
            endpoint = f"/simple/price?ids={coin_id}&vs_currencies={currency}"
            price_data = await self._get(endpoint)
            
            # If successful, cache the result
            if price_data and coin_id in price_data:
                self.cache.set(cache_key, price_data, self.cache.PRICE_TTL)
                return price_data
            
            # If the API returned successfully but no data for our coin,
            # return the cached data or empty result
            if cached_price and coin_id in cached_price:
                return cached_price
            return {}
            
        except Exception as e:
            # If there was an API error and we have cached data, return that instead
            if cached_price and coin_id in cached_price:
                return cached_price
            
            raise e
