from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
import sqlite3

query_editor_bp = Blueprint("query_editor", __name__)

def get_db_connection():
    """
    Establish and return a database connection.
    Replace 'metadata.db' with your actual database or connection string.
    """
    conn = sqlite3.connect('metadata.db')
    conn.row_factory = sqlite3.Row
    return conn

def convert_nl_to_sql(nl_query):
    """
    Stub function for converting natural language queries to SQL.
    In production, replace this with integration to an NLP model or rule-based parser.
    """
    if "sales" in nl_query.lower():
        return "SELECT * FROM sales_data LIMIT 10;"
    elif "orders" in nl_query.lower():
        return "SELECT * FROM orders LIMIT 10;"
    else:
        # Default fallback SQL query.
        return "SELECT * FROM sales_data LIMIT 10;"

@query_editor_bp.route("/query-editor")
@login_required
def query_editor():
    return render_template("core/query_editor.html")

@query_editor_bp.route("/run-manual-query", methods=["POST"])
@login_required
def run_manual_query():
    data = request.get_json()
    query = data.get("query")
    if not query:
        return jsonify({"error": "No query provided"}), 400
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        result = [dict(row) for row in rows]
        conn.close()
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@query_editor_bp.route("/run-nl-query", methods=["POST"])
@login_required
def run_nl_query():
    data = request.get_json()
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    try:
        sql_query = convert_nl_to_sql(prompt)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(sql_query)
        rows = cur.fetchall()
        result = [dict(row) for row in rows]
        conn.close()
        return jsonify({"sql": sql_query, "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
