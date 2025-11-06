from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.user import User

router = APIRouter()

@router.get("/")
def get_leaderboard(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    print("🔍 DEBUG: Getting leaderboard - simple version")
    
    try:
        # Simple query - just get users ordered by eco_score
        users = db.query(User).order_by(
            User.eco_score.desc()
        ).offset(skip).limit(limit).all()
        
        print(f"🔍 DEBUG: Found {len(users)} total users")
        
        leaderboard_data = []
        for idx, user in enumerate(users):
            leaderboard_data.append({
                "rank": idx + 1 + skip,
                "username": user.username,
                "full_name": user.full_name or user.username,
                "eco_score": float(user.eco_score or 0),
                "emissions_saved": float(user.total_emissions_saved or 0),
            })
        
        print(f"🔍 DEBUG: Returning {len(leaderboard_data)} leaderboard entries")
        return leaderboard_data
        
    except Exception as e:
        print(f"❌ ERROR in leaderboard: {e}")
        import traceback
        traceback.print_exc()
        return []