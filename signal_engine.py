import ta
import pandas as pd

def get_signal(df: pd.DataFrame) -> str:
    close = df['close']
    high = df['high']
    low = df['low']
    df['rsi'] = ta.momentum.RSIIndicator(close, window=14).rsi()
    df['ema_fast'] = ta.trend.EMAIndicator(close, window=9).ema_indicator()
    df['ema_slow'] = ta.trend.EMAIndicator(close, window=21).ema_indicator()
    macd = ta.trend.MACD(close, window_slow=26, window_fast=12, window_sign=9)
    df['macd_diff'] = macd.macd_diff()
    bb = ta.volatility.BollingerBands(close, window=20, window_dev=2)
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()
    stoch = ta.momentum.StochasticOscillator(high, low, close, window=14, smooth_window=3)
    df['stoch_k'] = stoch.stoch()
    df['stoch_d'] = stoch.stoch_signal()
    df['cci'] = ta.trend.CCIIndicator(high, low, close, window=20).cci()
    df['williams'] = ta.momentum.WilliamsRIndicator(high, low, close, lbp=14).williams_r()
    df['atr'] = ta.volatility.AverageTrueRange(high, low, close, window=14).average_true_range()
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    rsi = latest['rsi']
    price = latest['close']
    ema_fast = latest['ema_fast']
    ema_slow = latest['ema_slow']
    macd_diff = latest['macd_diff']
    macd_prev = prev['macd_diff']
    bb_upper = latest['bb_upper']
    bb_lower = latest['bb_lower']
    stoch_k = latest['stoch_k']
    stoch_d = latest['stoch_d']
    cci = latest['cci']
    williams = latest['williams']
    atr = latest['atr']
    buy_score = sum([rsi < 30, ema_fast > ema_slow, macd_diff > 0 and macd_diff > macd_prev, price <= bb_lower, stoch_k < 20 and stoch_d < 20, cci < -100, williams < -80, price > ema_slow])
    sell_score = sum([rsi > 70, ema_fast < ema_slow, macd_diff < 0 and macd_diff < macd_prev, price >= bb_upper, stoch_k > 80 and stoch_d > 80, cci > 100, williams > -20, price < ema_slow])
    total = 8
    direction = "buy" if buy_score >= sell_score else "sell"
    dominant = max(buy_score, sell_score)
    vol_ratio = (atr / price) * 1000
    probability = min(95, round((dominant / total) * 100 + max(0, 5 - vol_ratio)))
    if dominant >= 7:
        duration = "5 - 10 دقائق"
    elif dominant >= 5:
        duration = "10 - 15 دقيقة"
    elif dominant >= 3:
        duration = "15 - 30 دقيقة"
    else:
        duration = "غير محدد"
    stars = "⭐" * dominant + "☆" * (total - dominant)
    rsi_bar = _bar(rsi, 0, 100)
    details = (f"\n\n📊 *تحليل المؤشرات ({dominant}/{total}):*\n• RSI `{rsi:.1f}` {rsi_bar}\n• EMA: {'📈 صاعد' if ema_fast > ema_slow else '📉 هابط'}\n• MACD: {'↑ إيجابي' if macd_diff > 0 else '↓ سلبي'}\n• Bollinger: {'عند الدعم 🟢' if price <= bb_lower else 'عند المقاومة 🔴' if price >= bb_upper else 'وسط النطاق ⚪'}\n• Stochastic: `{stoch_k:.1f}` {'ذروة بيع' if stoch_k < 20 else 'ذروة شراء' if stoch_k > 80 else 'محايد'}\n• CCI: `{cci:.0f}` {'↑' if cci > 0 else '↓'}\n• Williams %R: `{williams:.1f}`\n\n⏱ *مدة الصفقة:* {duration}\n🎯 *نسبة النجاح:* `{probability}%`\n💪 *قوة الإشارة:* {stars}")
    if direction == "buy" and dominant >= 6:
        return f"🔼 *إشارة شراء قوية جداً* 🚀{details}"
    elif direction == "buy" and dominant >= 4:
        return f"🔼 *إشارة شراء* ✅{details}"
    elif direction == "sell" and dominant >= 6:
        return f"🔽 *إشارة بيع قوية جداً* 🚀{details}"
    elif direction == "sell" and dominant >= 4:
        return f"🔽 *إشارة بيع* ✅{details}"
    else:
        return f"⚠️ *السوق محايد — لا تدخل الآن*{details}"

def _bar(value, min_val, max_val, length=8):
    pct = (value - min_val) / (max_val - min_val)
    filled = max(0, min(length, int(pct * length)))
    return f"[{'█' * filled}{'░' * (length - filled)}]"
