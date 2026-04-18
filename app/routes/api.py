from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
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


@router.get("/player-stats/{player_id}")
async def get_player_stats(player_id: str):
    """
    Get detailed statistics for a specific player by ID.
    
    Args:
        player_id: The unique identifier of the player
        
    Returns:
        Player statistics including name, stats, and other relevant data
    """
    try:
        if not player_id or len(player_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="Player ID is required and cannot be empty")
        
        # Fetch player from database
        player = players_collection.find_one(
            {"playerId": player_id},
            {"_id": 0}  # Exclude MongoDB's internal ID
        )
        
        if not player:
            raise HTTPException(
                status_code=404,
                detail=f"Player with ID '{player_id}' not found in database"
            )
        
        return {
            "status": "success",
            "data": player
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching player statistics: {str(e)}"
        )


@router.get("/player-summary/{player_id}")
async def get_player_summary(player_id: str):
    """
    Get a summary of player statistics (name, basic stats only).
    
    Args:
        player_id: The unique identifier of the player
        
    Returns:
        Summarized player information
    """
    try:
        if not player_id or len(player_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="Player ID is required")
        
        player = players_collection.find_one(
            {"playerId": player_id},
            {
                "_id": 0,
                "playerId": 1,
                "playerName": 1,
                "role": 1,
                "team": 1,
                "country": 1,
                "stats": 1
            }
        )
        
        if not player:
            raise HTTPException(status_code=404, detail=f"Player with ID '{player_id}' not found")
        
        return {
            "status": "success",
            "data": player
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching player summary: {str(e)}")


@router.get("/search")
async def search_players(query: str):
    """
    Search for players by name.
    
    Args:
        query: Player name or partial name to search for
        
    Returns:
        List of players matching the search query
    """
    try:
        if not query or len(query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Search query is required")
        
        # Perform case-insensitive search
        players = list(players_collection.find(
            {"playerName": {"$regex": query, "$options": "i"}},
            {"_id": 0, "playerId": 1, "playerName": 1, "role": 1, "team": 1}
        ).limit(10))
        
        if not players:
            return {
                "status": "info",
                "message": f"No players found matching '{query}'",
                "data": []
            }
        
        return {
            "status": "success",
            "message": f"Found {len(players)} player(s)",
            "data": players
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching players: {str(e)}")


@router.get("/current-player-stats")
async def get_current_player_stats():
    """
    Get the statistics of the currently selected player.
    Checks the selected_player collection to get the player ID,
    then fetches the player's stats from the players collection.
    
    Returns:
        Player statistics if a player is selected, otherwise a message indicating no player is selected
    """
    try:
        # Get the currently selected player
        selected = selected_player_collection.find_one({"_id": "current"})
        
        if not selected:
            return {
                "status": "info",
                "message": "No player selected",
                "data": None
            }
        
        # Get the player ID from the selected player
        player_id = selected.get("playerId")
        
        if not player_id:
            return {
                "status": "error",
                "message": "Selected player has no ID",
                "data": None
            }
        
        # Fetch the player's stats from the players collection
        player = players_collection.find_one(
            {"playerId": player_id},
            {"_id": 0}
        )
        
        if not player:
            return {
                "status": "error",
                "message": f"Player with ID '{player_id}' not found in database",
                "data": None
            }
        
        return {
            "status": "success",
            "data": player
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching current player stats: {str(e)}")
