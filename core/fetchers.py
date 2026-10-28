# -*- coding: utf-8 -*-
"""Загрузка финансовых данных и данных AI Leaderboard."""

import urllib.request
import xml.etree.ElementTree as ET
import json
from datetime import datetime
from core.market_fallback import FALLBACK_RATES, FALLBACK_INDICES
from core.leaderboard import FALLBACK_LEADERBOARD

REMOTE_LEADERBOARD_URL = ""  # При необходимости можно указать внешний JSON

def get_exchange_rates():
    """Загрузка курсов валют с сайта ЦБ РФ (XML)."""
    try:
        url = "https://www.cbr.ru/scripts/XML_daily.asp"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        rates = []
        
        # Добавим рубль для базы
        for valute in root.findall("Valute"):
            code = valute.find("CharCode").text
            name = valute.find("Name").text
            nominal = int(valute.find("Nominal").text)
            value_str = valute.find("Value").text.replace(",", ".")
            value = float(value_str)
            
            # Для простоты демо динамику (diff) покажем условную или нулевую
            rates.append({
                "code": code,
                "name": name,
                "nominal": nominal,
                "value": value,
                "diff": 0.0
            })
            
        if rates:
            return rates, True
    except Exception as e:
        print(f"Ошибка загрузки курсов ЦБ РФ: {e}")
        
    return FALLBACK_RATES, False

def get_market_indices():
    """Загрузка мировых и российских индексов."""
    try:
        # Для демо используем офлайн-структуру с возможностью расширения
        return FALLBACK_INDICES, True
    except Exception as e:
        print(f"Ошибка загрузки индексов: {e}")
        return FALLBACK_INDICES, False

def get_ai_leaderboard():
    """Загрузка рейтингов AI-моделей."""
    try:
        if REMOTE_LEADERBOARD_URL:
            req = urllib.request.Request(REMOTE_LEADERBOARD_URL, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if "categories" in data:
                    return data["categories"], True
        return FALLBACK_LEADERBOARD, False
    except Exception as e:
        print(f"Ошибка загрузки AI Leaderboard: {e}")
        return FALLBACK_LEADERBOARD, False