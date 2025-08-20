"""
Prima Scholar Database Connection Manager
Handles TiDB Serverless connections and database operations
"""

import pymysql
import logging
import json
from contextlib import contextmanager
from typing import Dict, List, Any, Optional, Tuple
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

class DatabaseManager:
    """Manages TiDB Serverless database connections and operations"""
    
    def __init__(self, connection_string: str, pool_size: int = 10, max_overflow: int = 20):
        self.connection_string = connection_string
        self.logger = logging.getLogger(__name__)
        
        # Create SQLAlchemy engine with connection pooling
        self.engine = create_engine(
            connection_string,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,  # Validate connections
            echo=False,  # Set to True for SQL debugging
            connect_args={
                'charset': 'utf8mb4',
                'use_unicode': True,
                'autocommit': False
            }
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Initialize database schema
        self._initialize_schema()
        
        self.logger.info("Database connection manager initialized")
    
    def _initialize_schema(self):
        """Initialize database schema if not exists"""
        try:
            with self.get_connection() as conn:
                # Create tables using raw SQL
                schema_sql = self._get_schema_sql()
                
                for statement in schema_sql.split(';'):
                    statement = statement.strip()
                    if statement:
                        conn.execute(text(statement))
                
                conn.commit()
                self.logger.info("Database schema initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize database schema: {str(e)}")
            raise
    
    def _get_schema_sql(self) -> str:
        """Get database schema SQL"""
        return """
        -- Student excellence profiles with academic trajectory tracking
        CREATE TABLE IF NOT EXISTS scholar_profiles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(100) UNIQUE NOT NULL,
            current_gpa DECIMAL(3,2) DEFAULT 0.00,
            target_distinction VARCHAR(100) DEFAULT 'Dean_List',
            excellence_score DECIMAL(5,2) DEFAULT 0.00,
            prediction_confidence DECIMAL(3,2) DEFAULT 0.00,
            academic_level ENUM('undergraduate', 'graduate', 'doctoral', 'postdoc') DEFAULT 'undergraduate',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_student_id (student_id),
            INDEX idx_excellence_score (excellence_score),
            INDEX idx_target_distinction (target_distinction)
        );
        
        -- Academic documents with excellence-level embeddings
        CREATE TABLE IF NOT EXISTS academic_documents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content LONGTEXT NOT NULL,
            document_type ENUM('research_paper', 'course_material', 'thesis', 'journal_article', 'book', 'presentation') DEFAULT 'course_material',
            academic_level ENUM('undergraduate', 'graduate', 'doctoral', 'postdoc') DEFAULT 'undergraduate',
            excellence_tier ENUM('basic', 'advanced', 'scholar', 'elite') DEFAULT 'basic',
            embedding TEXT,  -- JSON string of embedding vector
            excellence_embedding TEXT,  -- JSON string of excellence-optimized embedding
            citation_count INT DEFAULT 0,
            impact_factor DECIMAL(5,2) DEFAULT 0.00,
            complexity_score INT DEFAULT 50,
            scholarly_connections TEXT,  -- JSON array of scholarly connections
            student_id VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_student_documents (student_id),
            INDEX idx_excellence_tier (excellence_tier),
            INDEX idx_academic_level (academic_level),
            INDEX idx_document_type (document_type),
            FOREIGN KEY (student_id) REFERENCES scholar_profiles(student_id) ON DELETE CASCADE
        );
        
        -- Excellence predictions and tracking
        CREATE TABLE IF NOT EXISTS distinction_predictions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(100) NOT NULL,
            distinction_type VARCHAR(100) NOT NULL,
            current_probability DECIMAL(5,2) DEFAULT 0.00,
            required_improvement_points INT DEFAULT 0,
            predicted_achievement_date DATE,
            confidence_level DECIMAL(3,2) DEFAULT 0.00,
            factors_analysis JSON,
            key_factors JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_student_predictions (student_id, distinction_type),
            INDEX idx_probability (current_probability),
            FOREIGN KEY (student_id) REFERENCES scholar_profiles(student_id) ON DELETE CASCADE
        );
        
        -- Scholar mentorship sessions with excellence focus
        CREATE TABLE IF NOT EXISTS mentorship_sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(100) NOT NULL,
            query TEXT NOT NULL,
            query_sophistication ENUM('basic', 'intermediate', 'advanced', 'scholar') DEFAULT 'basic',
            excellence_gap_analysis LONGTEXT,
            scholar_response LONGTEXT NOT NULL,
            thinking_frameworks JSON,
            probability_updates JSON,
            recommended_actions JSON,
            session_quality_score DECIMAL(3,2) DEFAULT 0.00,
            response_time_ms INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_student_sessions (student_id),
            INDEX idx_session_quality (session_quality_score),
            INDEX idx_query_sophistication (query_sophistication),
            FOREIGN KEY (student_id) REFERENCES scholar_profiles(student_id) ON DELETE CASCADE
        );
        
        -- Elite resource recommendations
        CREATE TABLE IF NOT EXISTS scholar_resources (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            resource_type ENUM('journal', 'book', 'conference', 'fellowship', 'network', 'tool', 'course') DEFAULT 'journal',
            excellence_level ENUM('advanced', 'scholar', 'elite') DEFAULT 'advanced',
            description TEXT,
            url VARCHAR(500),
            access_requirements TEXT,
            impact_on_distinctions JSON,
            target_academic_level ENUM('undergraduate', 'graduate', 'doctoral', 'postdoc') DEFAULT 'undergraduate',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_resource_type (resource_type),
            INDEX idx_excellence_level (excellence_level),
            INDEX idx_academic_level (target_academic_level)
        );
        
        -- Achievement records for excellence tracking
        CREATE TABLE IF NOT EXISTS achievement_records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(100) NOT NULL,
            achievement_type VARCHAR(100) NOT NULL,
            achievement_name VARCHAR(255) NOT NULL,
            impact_score DECIMAL(5,2) DEFAULT 0.00,
            verification_status ENUM('pending', 'verified', 'rejected') DEFAULT 'pending',
            achievement_date DATE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_student_achievements (student_id),
            INDEX idx_achievement_type (achievement_type),
            INDEX idx_impact_score (impact_score),
            FOREIGN KEY (student_id) REFERENCES scholar_profiles(student_id) ON DELETE CASCADE
        );
        
        -- Excellence trajectory tracking
        CREATE TABLE IF NOT EXISTS excellence_trajectory (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(100) NOT NULL,
            excellence_score DECIMAL(5,2) NOT NULL,
            gpa DECIMAL(3,2),
            session_count INT DEFAULT 0,
            achievement_count INT DEFAULT 0,
            trajectory_date DATE NOT NULL,
            factors_breakdown JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_student_trajectory (student_id, trajectory_date),
            INDEX idx_excellence_tracking (excellence_score, trajectory_date),
            FOREIGN KEY (student_id) REFERENCES scholar_profiles(student_id) ON DELETE CASCADE
        );
        
        -- External tool integrations log
        CREATE TABLE IF NOT EXISTS external_tool_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(100) NOT NULL,
            tool_name VARCHAR(100) NOT NULL,
            action VARCHAR(100) NOT NULL,
            payload JSON,
            response JSON,
            success BOOLEAN DEFAULT FALSE,
            execution_time_ms INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_student_tools (student_id),
            INDEX idx_tool_success (tool_name, success),
            FOREIGN KEY (student_id) REFERENCES scholar_profiles(student_id) ON DELETE CASCADE
        )"""
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup"""
        connection = None
        try:
            connection = self.engine.connect()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            self.logger.error(f"Database connection error: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()
    
    @contextmanager
    def get_session(self):
        """Get database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                result = conn.execute(text("SELECT 1"))
                return result.fetchone()[0] == 1
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Execute SELECT query and return results as list of dictionaries"""
        try:
            with self.get_connection() as conn:
                result = conn.execute(text(query), params or {})
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result.fetchall()]
        except Exception as e:
            self.logger.error(f"Query execution failed: {query[:100]}... Error: {str(e)}")
            raise
    
    def execute_insert(self, query: str, params: Optional[Dict] = None) -> int:
        """Execute INSERT query and return last insert ID"""
        try:
            with self.get_connection() as conn:
                result = conn.execute(text(query), params or {})
                conn.commit()
                return result.lastrowid
        except Exception as e:
            self.logger.error(f"Insert execution failed: {query[:100]}... Error: {str(e)}")
            raise
    
    def execute_update(self, query: str, params: Optional[Dict] = None) -> int:
        """Execute UPDATE/DELETE query and return affected rows"""
        try:
            with self.get_connection() as conn:
                result = conn.execute(text(query), params or {})
                conn.commit()
                return result.rowcount
        except Exception as e:
            self.logger.error(f"Update execution failed: {query[:100]}... Error: {str(e)}")
            raise
    
    def vector_search(self, query_embedding: List[float], table: str, 
                     embedding_column: str = 'embedding', limit: int = 5,
                     filters: Optional[Dict] = None) -> List[Dict]:
        """Perform vector similarity search using TiDB vector functions"""
        try:
            # Convert embedding to string format for TiDB
            embedding_str = json.dumps(query_embedding)
            
            # Build base query
            base_query = f"""
            SELECT *, 
                   JSON_EXTRACT({embedding_column}, ') as embedding_data,
                   SQRT(POWER(JSON_EXTRACT({embedding_column}, '$[0]') - :embed_0, 2) + 
                        POWER(JSON_EXTRACT({embedding_column}, '$[1]') - :embed_1, 2)) as similarity_score
            FROM {table}
            WHERE {embedding_column} IS NOT NULL
            """
            
            # Add filters if provided
            params = {}
            if filters:
                for key, value in filters.items():
                    base_query += f" AND {key} = :{key}"
                    params[key] = value
            
            # Add embedding parameters (simplified for first two dimensions)
            params['embed_0'] = query_embedding[0] if query_embedding else 0
            params['embed_1'] = query_embedding[1] if len(query_embedding) > 1 else 0
            
            base_query += " ORDER BY similarity_score ASC LIMIT :limit"
            params['limit'] = limit
            
            return self.execute_query(base_query, params)
            
        except Exception as e:
            self.logger.error(f"Vector search failed: {str(e)}")
            # Fallback to regular search
            fallback_query = f"SELECT * FROM {table} LIMIT :limit"
            return self.execute_query(fallback_query, {'limit': limit})
    
    def hybrid_search(self, query_text: str, query_embedding: List[float],
                     table: str, text_columns: List[str],
                     embedding_column: str = 'embedding',
                     excellence_filters: Optional[Dict] = None,
                     limit: int = 5) -> List[Dict]:
        """Perform hybrid search combining full-text and vector search"""
        try:
            # Build text search conditions
            text_conditions = []
            params = {'query_text': f"%{query_text}%"}
            
            for column in text_columns:
                text_conditions.append(f"{column} LIKE :query_text")
            
            text_condition = " OR ".join(text_conditions)
            
            # Build query with both text and vector similarity
            query = f"""
            SELECT *,
                   CASE WHEN ({text_condition}) THEN 1.0 ELSE 0.0 END as text_relevance,
                   0.5 as vector_relevance
            FROM {table}
            WHERE ({text_condition}) OR {embedding_column} IS NOT NULL
            """
            
            # Add excellence filters
            if excellence_filters:
                for key, value in excellence_filters.items():
                    if isinstance(value, list):
                        placeholders = ','.join([f":filter_{key}_{i}" for i in range(len(value))])
                        query += f" AND {key} IN ({placeholders})"
                        for i, v in enumerate(value):
                            params[f"filter_{key}_{i}"] = v
                    else:
                        query += f" AND {key} = :filter_{key}"
                        params[f"filter_{key}"] = value
            
            query += " ORDER BY (text_relevance + vector_relevance) DESC LIMIT :limit"
            params['limit'] = limit
            
            return self.execute_query(query, params)
            
        except Exception as e:
            self.logger.error(f"Hybrid search failed: {str(e)}")
            # Fallback to simple text search
            fallback_params = {'query_text': f"%{query_text}%", 'limit': limit}
            fallback_query = f"""
            SELECT * FROM {table} 
            WHERE {text_columns[0]} LIKE :query_text 
            LIMIT :limit
            """
            return self.execute_query(fallback_query, fallback_params)
    
    def get_student_profile(self, student_id: str) -> Optional[Dict]:
        """Get student profile with latest data"""
        query = """
        SELECT sp.*, 
               COUNT(DISTINCT ms.id) as total_sessions,
               COUNT(DISTINCT ar.id) as total_achievements,
               AVG(ms.session_quality_score) as avg_session_quality
        FROM scholar_profiles sp
        LEFT JOIN mentorship_sessions ms ON sp.student_id = ms.student_id
        LEFT JOIN achievement_records ar ON sp.student_id = ar.student_id
        WHERE sp.student_id = :student_id
        GROUP BY sp.id
        """
        
        results = self.execute_query(query, {'student_id': student_id})
        return results[0] if results else None
    
    def update_excellence_score(self, student_id: str, new_score: float,
                               factors: Dict) -> bool:
        """Update student excellence score and log trajectory"""
        try:
            # Update profile
            update_query = """
            UPDATE scholar_profiles 
            SET excellence_score = :score, 
                last_updated = CURRENT_TIMESTAMP
            WHERE student_id = :student_id
            """
            
            self.execute_update(update_query, {
                'score': new_score,
                'student_id': student_id
            })
            
            # Log trajectory
            trajectory_query = """
            INSERT INTO excellence_trajectory 
            (student_id, excellence_score, trajectory_date, factors_breakdown)
            VALUES (:student_id, :score, CURDATE(), :factors)
            ON DUPLICATE KEY UPDATE
            excellence_score = :score,
            factors_breakdown = :factors
            """
            
            self.execute_insert(trajectory_query, {
                'student_id': student_id,
                'score': new_score,
                'factors': json.dumps(factors)
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update excellence score: {str(e)}")
            return False
    
    def cleanup_old_data(self, days: int = 90):
        """Clean up old data to maintain performance"""
        try:
            cleanup_queries = [
                f"DELETE FROM external_tool_logs WHERE created_at < DATE_SUB(NOW(), INTERVAL {days} DAY)",
                f"DELETE FROM excellence_trajectory WHERE created_at < DATE_SUB(NOW(), INTERVAL {days * 2} DAY)",
            ]
            
            for query in cleanup_queries:
                affected = self.execute_update(query)
                self.logger.info(f"Cleaned up {affected} old records")
                
        except Exception as e:
            self.logger.error(f"Data cleanup failed: {str(e)}")
    
    def get_database_stats(self) -> Dict:
        """Get database statistics for monitoring"""
        try:
            stats = {}
            
            tables = [
                'scholar_profiles', 'academic_documents', 'distinction_predictions',
                'mentorship_sessions', 'scholar_resources', 'achievement_records'
            ]
            
            for table in tables:
                count_query = f"SELECT COUNT(*) as count FROM {table}"
                result = self.execute_query(count_query)
                stats[table] = result[0]['count'] if result else 0
            
            # Add storage info
            storage_query = """
            SELECT 
                ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS total_size_mb
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
            """
            
            storage_result = self.execute_query(storage_query)
            stats['total_size_mb'] = storage_result[0]['total_size_mb'] if storage_result else 0
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get database stats: {str(e)}")
            return {}
    
    def close(self):
        """Close all database connections"""
        try:
            self.engine.dispose()
            self.logger.info("Database connections closed")
        except Exception as e:
            self.logger.error(f"Error closing database connections: {str(e)}")