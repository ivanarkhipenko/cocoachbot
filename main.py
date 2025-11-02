# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List
import calendar

app = FastAPI(title="tg-calendar")

class DatesIn(BaseModel):
    dates: List[str]

def build_calendar(dates: List[str]) -> str:
    if not dates:
        raise HTTPException(status_code=400, detail="Массив дат пуст.")
    parsed = []
    for d in dates:
        try:
            dt = datetime.strptime(d, "%d-%m-%Y")
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Неверный формат даты: {d}. Используй DD-MM-YYYY.")
        parsed.append(dt)

    year = parsed[0].year
    month = parsed[0].month
    for dt in parsed[1:]:
        if dt.year != year or dt.month != month:
            raise HTTPException(status_code=400, detail="Все даты должны быть в одном месяце и году.")

    marked_days = {dt.day for dt in parsed}

    cal = calendar.Calendar(firstweekday=0)  # 0 - понедельник
    lines: List[str] = []
    lines.append(f"Календарь активностей для {year:04d}-{month:02d}:")
    lines.append("Пн Вт Ср Чт Пт Сб Вс")

    for week in cal.monthdayscalendar(year, month):
        row_parts = []
        for day in week:
            if day == 0:
                row_parts.append("  ")
            elif day in marked_days:
                row_parts.append("✅")
            else:
                if day < 10:
                    row_parts.append(f"{day} ")
                else:
                    row_parts.append(str(day))
        lines.append(" ".join(row_parts).rstrip())

    return "\n".join(lines)

@app.post("/calendar")
def get_calendar(body: DatesIn):
    text = build_calendar(body.dates)
    return {"text": text}
