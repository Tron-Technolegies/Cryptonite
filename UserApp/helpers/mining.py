import re

def parse_hashrate(hashrate_str):
    """
    Extract numeric value from '120 TH/s'
    """
    match = re.search(r'(\d+\.?\d*)', str(hashrate_str))
    return float(match.group(1)) if match else 0.0



import requests
from django.core.cache import cache

COINGECKO_API = "https://api.coingecko.com/api/v3"
CACHE_DURATION = 300  # 5 minutes

def get_btc_price():
    cache_key = "btc_price_usd"
    cached = cache.get(cache_key)

    if cached:
        return cached

    try:
        response = requests.get(
            f"{COINGECKO_API}/simple/price",
            params={"ids": "bitcoin", "vs_currencies": "usd"},
            timeout=10
        )
        response.raise_for_status()
        price = response.json()["bitcoin"]["usd"]

        cache.set(cache_key, price, CACHE_DURATION)
        return price

    except Exception:
        # fallback
        return 95000





def calculate_profitability(
    hashrate_th,
    power_watts,
    btc_price,
    number_of_miners=1,
    electricity_cost=0.058
):
    NETWORK_HASHRATE = 600_000_000  # TH/s
    BLOCK_REWARD = 3.125
    BLOCKS_PER_DAY = 144

    power_kw = power_watts / 1000

    coins_per_day_single = (
        (hashrate_th / NETWORK_HASHRATE)
        * BLOCK_REWARD
        * BLOCKS_PER_DAY
    )

    coins_per_day_single = round(coins_per_day_single, 8)

    daily_revenue = round(coins_per_day_single * btc_price, 2)
    daily_power_cost = round(power_kw * 24 * electricity_cost, 2)
    daily_profit = round(daily_revenue - daily_power_cost, 2)

    return {
        "salesDay": round(daily_revenue * number_of_miners, 2),
        "dayCosts": round(daily_power_cost * number_of_miners, 2),
        "winningDay": round(daily_profit * number_of_miners, 2),
        "monthlyRevenue": round(daily_revenue * number_of_miners * 30, 2),
        "monthlyCosts": round(daily_power_cost * number_of_miners * 30, 2),
        "profitMonth": round(daily_profit * number_of_miners * 30, 2),
        "dailyProfit": daily_profit,
        "coinsPerDay": round(coins_per_day_single * number_of_miners, 8),
    }

