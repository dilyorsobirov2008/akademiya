import pandas as pd
import os
from sqlalchemy import select
from database.models import User
from datetime import datetime

async def export_users_to_excel(session):
    stmt = select(User)
    result = await session.execute(stmt)
    users = result.scalars().all()
    
    data = []
    for user in users:
        data.append({
            "F.I.Sh": user.full_name,
            "Telefon": user.phone,
            "Filial": user.branch,
            "Bo'lim": user.department,
            "Lavozim": user.position,
            "Ishga kirgan sana": user.hire_date.strftime("%d.%m.%Y") if user.hire_date else "—",
            "Bevosita rahbar": user.manager_name,
            "Mentor": user.mentor_name,
            "Rol": user.role.value,
            "Ro'yxatdan o'tgan": user.created_at.strftime("%d.%m.%Y") if user.created_at else "—"
        })
    
    df = pd.DataFrame(data)
    file_path = f"data/users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    # Ensure directory exists
    os.makedirs("data", exist_ok=True)
    
    df.to_excel(file_path, index=False)
    return file_path
