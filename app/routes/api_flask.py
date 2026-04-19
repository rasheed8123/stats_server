from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime

# Load environment variables
load_dotenv()

api_bp = Blueprint('api', __name__)

# MongoDB connection
MONGO_URL = os.getenv("MONGODB_URL")
client = MongoClient(MONGO_URL)
db = client["cricket"]
players_collection = db["players"]
selected_player_collection = db["selected_player"]
query_tracking_collection = db["query_tracking"]

# Configure Groq API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = None

def get_groq_client():
    """Lazy load Groq client to avoid initialization errors"""
    global groq_client
    if groq_client is None and GROQ_API_KEY:
        groq_client = Groq(api_key=GROQ_API_KEY)
    return groq_client


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


@api_bp.route("/players-by-category", methods=["GET"])
def get_players_by_category():
    """Get list of players grouped by category"""
    try:
        # Fetch all players with required fields
        players = list(players_collection.find(
            {},
            {
                "_id": 0,
                "playerId": 1,
                "playerName": 1,
                "category": 1,
                "batting.sr": 1,
                "batting.runs": 1,
                "bowling.sr": 1,
                "bowling.wickets": 1
            }
        ))
        
        if not players:
            return jsonify({
                "status": "info",
                "message": "No players found",
                "data": {}
            }), 200
        
        # Group players by category
        grouped_players = {}
        for player in players:
            category = player.get("category", "uncategorized")
            if category not in grouped_players:
                grouped_players[category] = []
            
            grouped_players[category].append({
                "playerId": player.get("playerId"),
                "playerName": player.get("playerName"),
                "category": category,
                "batting": {
                    "sr": player.get("batting", {}).get("sr"),
                    "runs": player.get("batting", {}).get("runs")
                },
                "bowling": {
                    "sr": player.get("bowling", {}).get("sr"),
                    "wickets": player.get("bowling", {}).get("wickets")
                }
            })
        
        return jsonify({
            "status": "success",
            "message": f"Found {len(players)} player(s) across {len(grouped_players)} categor(ies)",
            "data": grouped_players
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "detail": f"Error fetching players by category: {str(e)}"}), 500


@api_bp.route("/chat", methods=["POST"])
def chat_with_player_info():
    """Chat endpoint that uses Groq to answer questions about a player with max 50 character response"""
    try:
        # Check if Groq API is configured
        if not GROQ_API_KEY:
            return jsonify({"status": "error", "detail": "GROQ_API_KEY environment variable not set"}), 500
        
        # Get JSON data from request body
        data = request.get_json()
        
        if not data:
            return jsonify({"status": "error", "detail": "Request body must be JSON"}), 400
        
        player_id = data.get("playerId", "").strip()
        user_query = data.get("query", "").strip()
        
        # Validation
        if not player_id or len(player_id) == 0:
            return jsonify({"status": "error", "detail": "Player ID is required"}), 400
        
        if not user_query or len(user_query) == 0:
            return jsonify({"status": "error", "detail": "Query is required"}), 400
        
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
        
        # Convert entire player document to string format for Groq
        import json
        player_info = json.dumps(player, indent=2, default=str)
        
        # System prompt for Groq
        system_prompt = """You are a cricket expert AI assistant. Answer questions about cricket players with detailed and informative responses.
Keep your response concise but descriptive - maximum 200 characters. Include relevant statistics or information when possible.
If the question cannot be answered with the given player data, say "No data available"."""
        
        # Create the prompt for Groq with full player document
        full_prompt = f"""{system_prompt}

Player Information (Complete Document):
{player_info}

User Question: {user_query}

Answer (max 200 characters):"""
        
        # Call Groq API
        client = get_groq_client()
        if not client:
            return jsonify({"status": "error", "detail": "Groq client not initialized"}), 500
        
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            model="llama-3.1-8b-instant"
        )
        
        # Get the response text and limit to 200 characters
        answer = response.choices[0].message.content.strip()
        if len(answer) > 200:
            answer = answer[:197] + "..."  # Truncate to 200 chars with ellipsis
        
        # Update query tracking collection
        query_doc = query_tracking_collection.find_one({"playerId": player_id})
        
        if query_doc:
            # Update existing document
            query_tracking_collection.update_one(
                {"playerId": player_id},
                {
                    "$set": {
                        "lastQuery": user_query,
                        "lastQueryTime": datetime.utcnow(),
                        "lastAnswer": answer
                    },
                    "$inc": {"queryCount": 1},
                    "$push": {
                        "queryHistory": {
                            "query": user_query,
                            "answer": answer,
                            "timestamp": datetime.utcnow()
                        }
                    }
                }
            )
        else:
            # Create new document for this player
            query_tracking_collection.insert_one({
                "playerId": player_id,
                "playerName": player.get('playerName', 'N/A'),
                "queryCount": 1,
                "lastQuery": user_query,
                "lastAnswer": answer,
                "lastQueryTime": datetime.utcnow(),
                "queryHistory": [
                    {
                        "query": user_query,
                        "answer": answer,
                        "timestamp": datetime.utcnow()
                    }
                ]
            })
        
        return jsonify({
            "status": "success",
            "data": {
                "playerId": player_id,
                "playerName": player.get('playerName'),
                "query": user_query,
                "answer": answer,
                "characterCount": len(answer)
            }
        }), 200
        
    except Exception as e:
        import traceback
        error_detail = f"Error processing chat request: {str(e)}"
        print(f"Chat API Error: {traceback.format_exc()}")
        return jsonify({"status": "error", "detail": error_detail, "error_trace": str(traceback.format_exc())}), 500


@api_bp.route("/player-query-stats/<player_id>", methods=["GET"])
def get_player_query_stats(player_id):
    """Get query tracking statistics for a specific player"""
    try:
        if not player_id or len(player_id.strip()) == 0:
            return jsonify({"status": "error", "detail": "Player ID is required"}), 400
        
        query_stats = query_tracking_collection.find_one(
            {"playerId": player_id},
            {"_id": 0}
        )
        
        if not query_stats:
            return jsonify({
                "status": "info",
                "message": f"No query history found for player '{player_id}'",
                "data": None
            }), 200
        
        return jsonify({
            "status": "success",
            "data": query_stats
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "detail": f"Error fetching query stats: {str(e)}"}), 500


@api_bp.route("/trending-players", methods=["GET"])
def get_trending_players():
    """Get top 3 trending players with their most asked questions analyzed by Groq"""
    try:
        if not GROQ_API_KEY:
            return jsonify({"status": "error", "detail": "GROQ_API_KEY environment variable not set"}), 500
        
        # Get top 3 players by query count
        top_players = list(query_tracking_collection.find(
            {},
            {"_id": 0}
        ).sort("queryCount", -1).limit(3))
        
        if not top_players:
            return jsonify({
                "status": "info",
                "message": "No query history found",
                "data": []
            }), 200
        
        trending_data = []
        
        for player_query_doc in top_players:
            player_id = player_query_doc.get("playerId")
            query_count = player_query_doc.get("queryCount", 0)
            query_history = player_query_doc.get("queryHistory", [])
            
            # Fetch full player details
            player_details = players_collection.find_one(
                {"playerId": player_id},
                {"_id": 0}
            )
            
            if not player_details:
                continue
            
            # Find most asked question by counting occurrences
            most_asked_question = None
            if query_history:
                query_counts = {}
                for q in query_history:
                    question = q.get("query", "")
                    query_counts[question] = query_counts.get(question, 0) + 1
                
                # Get the most frequently asked question
                most_asked_question = max(query_counts, key=query_counts.get)
            
            # Use Groq to summarize the most asked question insight
            most_asked_summary = None
            if most_asked_question:
                summary_prompt = f"""You are a cricket analyst. Based on this player and the most frequently asked question about them, provide a brief insight.

Player: {player_details.get('playerName', 'N/A')}
Most Asked Question: {most_asked_question}

Provide a 1-2 line insight about why this question is frequently asked about the player (max 150 characters):"""
                
                try:
                    client = get_groq_client()
                    if not client:
                        most_asked_summary = "Groq client not initialized"
                    else:
                        summary_response = client.chat.completions.create(
                            messages=[
                                {
                                    "role": "user",
                                    "content": summary_prompt
                                }
                            ],
                            model="llama-3.1-8b-instant"
                        )
                        most_asked_summary = summary_response.choices[0].message.content.strip()
                except Exception as groq_error:
                    most_asked_summary = f"Insight generation error: {str(groq_error)}"
            
            trending_data.append({
                "rank": len(trending_data) + 1,
                "playerId": player_id,
                "playerName": player_details.get('playerName', 'N/A'),
                "role": player_details.get('role', 'N/A'),
                "team": player_details.get('team', 'N/A'),
                "country": player_details.get('country', 'N/A'),
                "queryCount": query_count,
                "mostAskedQuestion": most_asked_question,
                "questionInsight": most_asked_summary,
                "playerDetails": player_details
            })
        
        return jsonify({
            "status": "success",
            "message": f"Top {len(trending_data)} trending players",
            "data": trending_data
        }), 200
        
    except Exception as e:
        import traceback
        error_detail = f"Error fetching trending players: {str(e)}"
        print(f"Trending Players API Error: {traceback.format_exc()}")
        return jsonify({"status": "error", "detail": error_detail, "error_trace": str(traceback.format_exc())}), 500
