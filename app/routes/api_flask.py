from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_bp = Blueprint('api', __name__)

# MongoDB connection
MONGO_URL = os.getenv("MONGODB_URL", "mongodb+srv://abdulrasheed8223:abdulrash@first.qez08g9.mongodb.net/bbl_season_4")
client = MongoClient(MONGO_URL)
db = client["cricket"]
players_collection = db["players"]
selected_player_collection = db["selected_player"]


@api_bp.route("/player-stats/<player_id>", methods=["GET"])
def get_player_stats(player_id):
    """Get detailed statistics for a specific player by ID"""
    try:
        if not player_id or len(player_id.strip()) == 0:
            return jsonify({"status": "error", "detail": "Player ID is required and cannot be empty"}), 400
        
        # Fetch player from database
        player = players_collection.find_one(
            {"playerId": player_id},
            {"_id": 0}
        )
        
        if not player:
            return jsonify({
                "status": "error",
                "detail": f"Player with ID '{player_id}' not found in database"
            }), 404
        
        return jsonify({"status": "success", "data": player}), 200
        
    except Exception as e:
        return jsonify({"status": "error", "detail": f"Error fetching player statistics: {str(e)}"}), 500


@api_bp.route("/player-summary/<player_id>", methods=["GET"])
def get_player_summary(player_id):
    """Get a summary of player statistics"""
    try:
        if not player_id or len(player_id.strip()) == 0:
            return jsonify({"status": "error", "detail": "Player ID is required"}), 400
        
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
            return jsonify({"status": "error", "detail": f"Player with ID '{player_id}' not found"}), 404
        
        return jsonify({"status": "success", "data": player}), 200
        
    except Exception as e:
        return jsonify({"status": "error", "detail": f"Error fetching player summary: {str(e)}"}), 500


@api_bp.route("/search", methods=["GET"])
def search_players():
    """Search for players by name"""
    try:
        query = request.args.get("query", "").strip()
        
        if not query or len(query) == 0:
            return jsonify({"status": "error", "detail": "Search query is required"}), 400
        
        # Perform case-insensitive search
        players = list(players_collection.find(
            {"playerName": {"$regex": query, "$options": "i"}},
            {"_id": 0, "playerId": 1, "playerName": 1, "role": 1, "team": 1}
        ).limit(10))
        
        if not players:
            return jsonify({
                "status": "info",
                "message": f"No players found matching '{query}'",
                "data": []
            }), 200
        
        return jsonify({
            "status": "success",
            "message": f"Found {len(players)} player(s)",
            "data": players
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "detail": f"Error searching players: {str(e)}"}), 500


@api_bp.route("/current-player-stats", methods=["GET"])
def get_current_player_stats():
    """Get the statistics of the currently selected player"""
    try:
        # Get the currently selected player
        selected = selected_player_collection.find_one({"_id": "current"})
        
        if not selected:
            return jsonify({
                "status": "info",
                "message": "No player selected",
                "data": None
            }), 200
        
        # Get the player ID from the selected player
        player_id = selected.get("playerId")
        
        if not player_id:
            return jsonify({
                "status": "error",
                "message": "Selected player has no ID",
                "data": None
            }), 200
        
        # Fetch the player's stats from the players collection
        player = players_collection.find_one(
            {"playerId": player_id},
            {"_id": 0}
        )
        
        if not player:
            return jsonify({
                "status": "error",
                "message": f"Player with ID '{player_id}' not found in database",
                "data": None
            }), 200
        
        return jsonify({"status": "success", "data": player}), 200
        
    except Exception as e:
        return jsonify({"status": "error", "detail": f"Error fetching current player stats: {str(e)}"}), 500
