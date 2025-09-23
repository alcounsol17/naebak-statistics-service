from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime, timedelta
import json
import threading

app = Flask(__name__)
CORS(app)

# Database configuration
DB_PATH = os.getenv('DB_PATH', 'statistics.db')
lock = threading.Lock()

def init_db():
    """Initialize the SQLite database"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Create statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                category TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create daily_stats table for time-series data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, metric_name, category)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_metric_name ON statistics(metric_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON statistics(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_date ON daily_stats(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_metric ON daily_stats(metric_name)')
        
        conn.commit()

# Initialize database on startup
init_db()

# الدالة المكررة محذوفة - سيتم استخدام الدالة المحسنة في الأسفل

@app.route('/stats', methods=['POST'])
def add_statistic():
    """Add or update a statistic"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        metric_name = data.get('metric_name')
        metric_value = data.get('metric_value')
        category = data.get('category', 'general')
        description = data.get('description', '')
        
        if not metric_name or metric_value is None:
            return jsonify({"error": "metric_name and metric_value are required"}), 400
        
        with lock:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                
                # Check if statistic exists
                cursor.execute(
                    'SELECT id FROM statistics WHERE metric_name = ? AND category = ?',
                    (metric_name, category)
                )
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing statistic
                    cursor.execute('''
                        UPDATE statistics 
                        SET metric_value = ?, description = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE metric_name = ? AND category = ?
                    ''', (metric_value, description, metric_name, category))
                else:
                    # Insert new statistic
                    cursor.execute('''
                        INSERT INTO statistics (metric_name, metric_value, category, description)
                        VALUES (?, ?, ?, ?)
                    ''', (metric_name, metric_value, category, description))
                
                conn.commit()
        
        return jsonify({
            "success": True,
            "metric_name": metric_name,
            "metric_value": metric_value,
            "category": category,
            "action": "updated" if existing else "created",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_statistics():
    """Get statistics with optional filtering"""
    try:
        category = request.args.get('category')
        metric_name = request.args.get('metric_name')
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            query = 'SELECT metric_name, metric_value, category, description, updated_at FROM statistics'
            params = []
            conditions = []
            
            if category:
                conditions.append('category = ?')
                params.append(category)
            
            if metric_name:
                conditions.append('metric_name = ?')
                params.append(metric_name)
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            
            query += ' ORDER BY category, metric_name'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            statistics = []
            for row in rows:
                statistics.append({
                    "metric_name": row[0],
                    "metric_value": row[1],
                    "category": row[2],
                    "description": row[3],
                    "updated_at": row[4]
                })
        
        return jsonify({
            "statistics": statistics,
            "count": len(statistics),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stats/daily', methods=['POST'])
def add_daily_stat():
    """Add daily statistic"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        metric_name = data.get('metric_name')
        metric_value = data.get('metric_value')
        category = data.get('category', 'general')
        
        if not metric_name or metric_value is None:
            return jsonify({"error": "metric_name and metric_value are required"}), 400
        
        with lock:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                
                # Insert or replace daily statistic
                cursor.execute('''
                    INSERT OR REPLACE INTO daily_stats (date, metric_name, metric_value, category)
                    VALUES (?, ?, ?, ?)
                ''', (date, metric_name, metric_value, category))
                
                conn.commit()
        
        return jsonify({
            "success": True,
            "date": date,
            "metric_name": metric_name,
            "metric_value": metric_value,
            "category": category,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stats/daily', methods=['GET'])
def get_daily_statistics():
    """Get daily statistics with optional date range"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        metric_name = request.args.get('metric_name')
        category = request.args.get('category')
        
        # Default to last 30 days if no dates provided
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT date, metric_name, metric_value, category, created_at 
                FROM daily_stats 
                WHERE date BETWEEN ? AND ?
            '''
            params = [start_date, end_date]
            
            if metric_name:
                query += ' AND metric_name = ?'
                params.append(metric_name)
            
            if category:
                query += ' AND category = ?'
                params.append(category)
            
            query += ' ORDER BY date DESC, metric_name'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            daily_stats = []
            for row in rows:
                daily_stats.append({
                    "date": row[0],
                    "metric_name": row[1],
                    "metric_value": row[2],
                    "category": row[3],
                    "created_at": row[4]
                })
        
        return jsonify({
            "daily_statistics": daily_stats,
            "count": len(daily_stats),
            "date_range": {
                "start_date": start_date,
                "end_date": end_date
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stats/summary', methods=['GET'])
def get_summary():
    """Get statistics summary by category"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Get summary by category
            cursor.execute('''
                SELECT category, COUNT(*) as count, AVG(metric_value) as avg_value,
                       MIN(metric_value) as min_value, MAX(metric_value) as max_value
                FROM statistics 
                GROUP BY category
                ORDER BY category
            ''')
            
            categories = []
            for row in cursor.fetchall():
                categories.append({
                    "category": row[0],
                    "count": row[1],
                    "avg_value": round(row[2], 2) if row[2] else 0,
                    "min_value": row[3],
                    "max_value": row[4]
                })
            
            # Get total count
            cursor.execute('SELECT COUNT(*) FROM statistics')
            total_stats = cursor.fetchone()[0]
            
            # Get recent updates
            cursor.execute('''
                SELECT metric_name, metric_value, category, updated_at
                FROM statistics 
                ORDER BY updated_at DESC 
                LIMIT 10
            ''')
            
            recent_updates = []
            for row in cursor.fetchall():
                recent_updates.append({
                    "metric_name": row[0],
                    "metric_value": row[1],
                    "category": row[2],
                    "updated_at": row[3]
                })
        
        return jsonify({
            "summary": {
                "total_statistics": total_stats,
                "categories": categories,
                "recent_updates": recent_updates
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def service_info():
    """Service information endpoint"""
    return jsonify({
        "service": "Naebak Statistics Service",
        "description": "خدمة الإحصائيات وعداد الزوار لمنصة نائبك.كوم - تتبع وإدارة جميع الإحصائيات والمقاييس",
        "version": "1.0.0",
        "status": "active",
        "technology": "Flask + SQLite",
        "endpoints": {
            "info": "/",
            "stats_create": "POST /stats",
            "stats_list": "GET /stats",
            "daily_stats_create": "POST /stats/daily",
            "daily_stats_list": "GET /stats/daily",
            "stats_summary": "GET /stats/summary",
            "health": "/health"
        },
        "features": [
            "إدارة الإحصائيات العامة",
            "تتبع الإحصائيات اليومية",
            "ملخص الإحصائيات حسب الفئة",
            "قاعدة بيانات SQLite محلية",
            "واجهات برمجية RESTful",
            "معالجة الأخطاء المتقدمة",
            "دعم CORS للتطبيقات الأمامية",
            "فحص صحة الخدمة"
        ],
        "database": {
            "type": "SQLite",
            "path": DB_PATH,
            "tables": ["statistics", "daily_stats"]
        },
        "documentation": "https://github.com/alcounsol17/naebak-statistics-service",
        "support": "https://naebak.com"
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # فحص قاعدة البيانات
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM statistics')
            stats_count = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM daily_stats')
            daily_count = cursor.fetchone()[0]
        
        return jsonify({
            "status": "healthy",
            "service": "Naebak Statistics Service",
            "version": "1.0.0",
            "database": {
                "status": "connected",
                "statistics_count": stats_count,
                "daily_stats_count": daily_count
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8007))  # تغيير المنفذ الافتراضي لتجنب التضارب
    debug = os.getenv('FLASK_ENV') == 'development'
    
    # تهيئة قاعدة البيانات عند بدء التطبيق
    init_db()
    
    print(f"🚀 Starting Naebak Statistics Service on port {port}")
    print(f"📊 Database: {DB_PATH}")
    print(f"🔧 Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
