from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

admin_bp = Blueprint('admin', __name__)

# MongoDB connection
MONGO_URL = os.getenv("MONGODB_URL", "mongodb+srv://abdulrasheed8223:abdulrash@first.qez08g9.mongodb.net/bbl_season_4")
client = MongoClient(MONGO_URL)
db = client["cricket"]
players_collection = db["players"]
selected_player_collection = db["selected_player"]


@admin_bp.route("/players", methods=["GET"])
def get_all_players():
    """Get list of all available players from the database"""
    try:
        players = list(players_collection.find({}, {"_id": 0, "playerId": 1, "playerName": 1}))
        if not players:
            return jsonify({"status": "error", "detail": "No players found in database"}), 404
        return jsonify({"status": "success", "data": players}), 200
    except Exception as e:
        return jsonify({"status": "error", "detail": f"Error fetching players: {str(e)}"}), 500


@admin_bp.route("/current-player", methods=["GET"])
def get_current_player():
    """Get the currently selected player"""
    try:
        selected = selected_player_collection.find_one({"_id": "current"})
        if not selected:
            return jsonify({
                "status": "info",
                "message": "No player selected yet",
                "data": None
            }), 200
        return jsonify({
            "status": "success",
            "data": {
                "playerId": selected.get("playerId"),
                "playerName": selected.get("playerName")
            }
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "detail": f"Error fetching current player: {str(e)}"}), 500


@admin_bp.route("/select-player", methods=["POST"])
def select_player():
    """Update the current player in the database"""
    try:
        data = request.get_json()
        
        if not data or not data.get("playerId") or not data.get("playerName"):
            return jsonify({"status": "error", "detail": "Player ID and name are required"}), 400
        
        player_id = data.get("playerId")
        player_name = data.get("playerName")
        
        # Verify player exists in database
        player = players_collection.find_one({"playerId": player_id})
        if not player:
            return jsonify({"status": "error", "detail": f"Player with ID {player_id} not found"}), 404
        
        # Update or insert current player in selected_player collection
        selected_player_collection.update_one(
            {"_id": "current"},
            {
                "$set": {
                    "playerId": player_id,
                    "playerName": player_name,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return jsonify({
            "status": "success",
            "message": f"Successfully selected player: {player_name}",
            "data": {
                "playerId": player_id,
                "playerName": player_name
            }
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "detail": f"Error selecting player: {str(e)}"}), 500


@admin_bp.route("/reset-player", methods=["DELETE"])
def reset_player():
    """Reset the current player selection"""
    try:
        selected_player_collection.delete_one({"_id": "current"})
        return jsonify({
            "status": "success",
            "message": "Player selection reset"
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "detail": f"Error resetting player: {str(e)}"}), 500
