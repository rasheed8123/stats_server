from fastapi import APIRouter, HTTPException, Body
from pymongo import MongoClient
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter()

# MongoDB connection
MONGO_URL = os.getenv("MONGODB_URL")
client = MongoClient(MONGO_URL)
db = client["cricket"]
players_collection = db["players"]
selected_player_collection = db["selected_player"]


class PlayerSelection(BaseModel):
    playerId: str
    playerName: str


@router.get("/players")
async def get_all_players():
    """Get list of all available players from the database"""
    try:
        players = list(players_collection.find({}, {"_id": 0, "playerId": 1, "playerName": 1}))
        if not players:
            raise HTTPException(status_code=404, detail="No players found in database")
        return {"status": "success", "data": players}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching players: {str(e)}")


@router.get("/current-player")
async def get_current_player():
    """Get the currently selected player"""
    try:
        selected = selected_player_collection.find_one({"_id": "current"})
        if not selected:
            return {
                "status": "info",
                "message": "No player selected yet",
                "data": None
            }
        return {"status": "success", "data": {"playerId": selected["playerId"], "playerName": selected["playerName"]}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching current player: {str(e)}")


@router.post("/select-player")
async def select_player(selection: PlayerSelection):
    """Update the current player in the database"""
    try:
        if not selection.playerId or not selection.playerName:
            raise HTTPException(status_code=400, detail="Player ID and name are required")
        
        # Verify player exists in database
        player = players_collection.find_one({"playerId": selection.playerId})
        if not player:
            raise HTTPException(status_code=404, detail=f"Player with ID {selection.playerId} not found")
        
        # Update or insert current player in selected_player collection
        result = selected_player_collection.update_one(
            {"_id": "current"},
            {
                "$set": {
                    "playerId": selection.playerId,
                    "playerName": selection.playerName,
                    "updated_at": __import__("datetime").datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return {
            "status": "success",
            "message": f"Successfully selected player: {selection.playerName}",
            "data": {
                "playerId": selection.playerId,
                "playerName": selection.playerName
            }
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error selecting player: {str(e)}")


@router.delete("/reset-player")
async def reset_player():
    """Reset the current player selection"""
    try:
        selected_player_collection.delete_one({"_id": "current"})
        return {
            "status": "success",
            "message": "Player selection reset"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting player: {str(e)}")
