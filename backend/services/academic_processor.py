"""
Prima Scholar Academic Document Processor
Processes academic documents with excellence-level classification and embeddings
"""

import fitz  # PyMuPDF
import openai
import logging
import json
import re
import os
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from docx import Document
import textract
import numpy as np

class AcademicProcessor:
    """Processes academic documents with excellence-aware analysis"""
    
    def __init__(self, openai_api_key: str, db_manager):
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
        
        # Excellence tier classification keywords
        self.excellence_keywords = {
            'elite': [
                'seminal', 'groundbreaking', 'paradigm', 'revolutionary',
                'fundamental theorem', 'novel framework', 'breakthrough',
                'theoretical foundation', 'empirical validation', 'meta-analysis'
            ],
            'scholar': [
                'theoretical framework', 'methodology', 'empirical analysis',
                'systematic approach', 'comprehensive review', 'analytical framework',
                'research methodology', 'statistical analysis', 'hypothesis testing'
            ],
            'advanced': [
                'complex analysis', 'sophisticated approach', 'comprehensive study',
                'in-depth analysis', 'advanced concepts', 'detailed examination',
                'rigorous analysis', 'systematic investigation'
            ],
            'basic': [
                'introduction', 'overview', 'basic concepts', 'fundamentals',
                'elementary', 'simple analysis', 'general overview', 'summary'
            ]
        }
        
        # Academic level indicators
        self.level_indicators = {
            'doctoral': [
                'dissertation', 'thesis defense', 'original research',
                'comprehensive examination', 'doctoral candidate'
            ],
            'graduate': [
                'master thesis', 'graduate seminar', 'advanced coursework',
                'research methods', 'graduate studies'
            ],
            'undergraduate': [
                'undergraduate research', 'senior project', 'capstone',
                'course project', 'term paper'
            ]
        }
        
        self.logger.info("Academic Processor initialized")
    
    def process_document(self, file_path: str, title: str, student_id: str) -> Dict:
        """Process academic document with excellence classification"""
        try:
            # Extract text content
            text_content = self._extract_text_from_file(file_path)
            if not text_content:
                return {'error': 'Could not extract text from document'}
            
            # Classify document
            document_type = self._classify_document_type(text_content, title)
            academic_level = self._classify_academic_level(text_content, title)
            excellence_tier = self._determine_excellence_tier(text_content)
            
            # Create scholarly chunks
            chunks = self._create_scholarly_chunks(text_content)
            
            # Generate embeddings
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                try:
                    # Standard embedding
                    standard_embedding = self._generate_standard_embedding(chunk)
                    
                    # Excellence-optimized embedding
                    excellence_embedding = self._generate_excellence_embedding(chunk, excellence_tier)
                    
                    # Analyze scholarly connections
                    scholarly_connections = self._identify_scholarly_connections(chunk)
                    
                    # Calculate complexity score
                    complexity_score = self._calculate_complexity_score(chunk)
                    
                    processed_chunk = {
                        'title': title,
                        'content': chunk,
                        'document_type': document_type,
                        'academic_level': academic_level,
                        'excellence_tier': excellence_tier,
                        'embedding': json.dumps(standard_embedding),
                        'excellence_embedding': json.dumps(excellence_embedding),
                        'scholarly_connections': json.dumps(scholarly_connections),
                        'complexity_score': complexity_score,
                        'chunk_index': i,
                        'student_id': student_id,
                        'citation_count': self._estimate_citation_potential(chunk),
                        'impact_factor': self._calculate_impact_factor(chunk, excellence_tier)
                    }
                    
                    processed_chunks.append(processed_chunk)
                    
                except Exception as e:
                    self.logger.error(f"Failed to process chunk {i}: {str(e)}")
                    continue
            
            if not processed_chunks:
                return {'error': 'No chunks could be processed'}
            
            # Store in database
            stored_ids = self._store_document_chunks(processed_chunks)
            
            # Update student's document statistics
            self._update_student_document_stats(student_id)
            
            return {
                'success': True,
                'document_title': title,
                'chunks_processed': len(processed_chunks),
                'document_type': document_type,
                'academic_level': academic_level,
                'excellence_tier': excellence_tier,
                'average_complexity': sum(c['complexity_score'] for c in processed_chunks) / len(processed_chunks),
                'stored_ids': stored_ids,
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Document processing failed: {str(e)}")
            return {'error': str(e)}
    
    def _extract_text_from_file(self, file_path: str) -> Optional[str]:
        """Extract text from various file formats"""
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                return self._extract_from_pdf(file_path)
            elif file_extension in ['.docx', '.doc']:
                return self._extract_from_docx(file_path)
            elif file_extension == '.txt':
                return self._extract_from_txt(file_path)
            else:
                # Fallback to textract for other formats
                try:
                    return textract.process(file_path).decode('utf-8')
                except Exception:
                    return None
                    
        except Exception as e:
            self.logger.error(f"Text extraction failed: {str(e)}")
            return None
    
    def _extract_from_pdf(self, file_path: str) -> Optional[str]:
        """Extract text from PDF using PyMuPDF"""
        try:
            doc = fitz.open(file_path)
            text = ""
            
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                text += page.get_text()
            
            doc.close()
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"PDF extraction failed: {str(e)}")
            return None
    
    def _extract_from_docx(self, file_path: str) -> Optional[str]:
        """Extract text from DOCX files"""
        try:
            doc = Document(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"DOCX extraction failed: {str(e)}")
            return None
    
    def _extract_from_txt(self, file_path: str) -> Optional[str]:
        """Extract text from plain text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            self.logger.error(f"TXT extraction failed: {str(e)}")
            return None
    
    def _classify_document_type(self, content: str, title: str) -> str:
        """Classify the type of academic document"""
        content_lower = content.lower()
        title_lower = title.lower()
        
        # Research paper indicators
        research_indicators = ['abstract', 'methodology', 'results', 'conclusion', 'references']
        if sum(1 for indicator in research_indicators if indicator in content_lower) >= 3:
            return 'research_paper'
        
        # Thesis indicators
        if any(word in title_lower for word in ['thesis', 'dissertation']):
            return 'thesis'
        
        # Journal article indicators
        if 'journal' in title_lower or 'volume' in content_lower:
            return 'journal_article'
        
        # Course material indicators
        if any(word in content_lower for word in ['syllabus', 'lecture', 'homework', 'assignment']):
            return 'course_material'
        
        # Book indicators
        if any(word in content_lower for word in ['chapter', 'isbn', 'publisher']):
            return 'book'
        
        # Presentation indicators
        if any(word in title_lower for word in ['presentation', 'slides', 'ppt']):
            return 'presentation'
        
        return 'course_material'  # Default
    
    def _classify_academic_level(self, content: str, title: str) -> str:
        """Classify the academic level of the document"""
        content_lower = content.lower()
        title_lower = title.lower()
        
        # Check for level indicators
        for level, indicators in self.level_indicators.items():
            if any(indicator in content_lower or indicator in title_lower for indicator in indicators):
                return level
        
        # Analyze complexity as fallback
        complexity_score = self._calculate_complexity_score(content)
        
        if complexity_score >= 80:
            return 'doctoral'
        elif complexity_score >= 65:
            return 'graduate'
        else:
            return 'undergraduate'
    
    def _determine_excellence_tier(self, content: str) -> str:
        """Classify content by academic excellence tier"""
        content_lower = content.lower()
        
        # Count keyword matches for each tier
        tier_scores = {}
        for tier, keywords in self.excellence_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            tier_scores[tier] = score
        
        # Additional sophistication factors
        sophistication_indicators = [
            'theoretical framework', 'empirical validation', 'meta-analysis',
            'statistical significance', 'peer review', 'systematic review'
        ]
        sophistication_count = sum(1 for indicator in sophistication_indicators 
                                 if indicator in content_lower)
        
        # Calculate complexity indicators
        sentence_count = len(re.split(r'[.!?]+', content))
        avg_sentence_length = len(content.split()) / max(sentence_count, 1)
        
        # Determine tier based on multiple factors
        if tier_scores['elite'] >= 3 or sophistication_count >= 4:
            return 'elite'
        elif tier_scores['scholar'] >= 2 or sophistication_count >= 2:
            return 'scholar'
        elif tier_scores['advanced'] >= 2 or avg_sentence_length > 25:
            return 'advanced'
        else:
            return 'basic'
    
    def _create_scholarly_chunks(self, content: str, max_chunk_size: int = 2000) -> List[str]:
        """Create semantically meaningful chunks for academic content"""
        # Split by academic sections first
        section_patterns = [
            r'\n\s*Abstract\s*\n',
            r'\n\s*Introduction\s*\n',
            r'\n\s*Methodology\s*\n',
            r'\n\s*Results\s*\n',
            r'\n\s*Discussion\s*\n',
            r'\n\s*Conclusion\s*\n',
            r'\n\s*References\s*\n'
        ]
        
        sections = [content]
        for pattern in section_patterns:
            new_sections = []
            for section in sections:
                new_sections.extend(re.split(pattern, section, flags=re.IGNORECASE))
            sections = new_sections
        
        # Further split large sections
        chunks = []
        for section in sections:
            if len(section) <= max_chunk_size:
                chunks.append(section.strip())
            else:
                # Split by paragraphs
                paragraphs = section.split('\n\n')
                current_chunk = ""
                
                for paragraph in paragraphs:
                    if len(current_chunk + paragraph) <= max_chunk_size:
                        current_chunk += paragraph + "\n\n"
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = paragraph + "\n\n"
                
                if current_chunk:
                    chunks.append(current_chunk.strip())
        
        # Filter out very short chunks
        return [chunk for chunk in chunks if len(chunk.split()) > 10]
    
    def _generate_standard_embedding(self, text: str) -> List[float]:
        """Generate standard OpenAI embedding"""
        try:
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        except Exception as e:
            self.logger.error(f"Standard embedding generation failed: {str(e)}")
            # Return zero vector as fallback
            return [0.0] * 1536
    
    def _generate_excellence_embedding(self, text: str, excellence_tier: str) -> List[float]:
        """Generate excellence-optimized embedding with academic context"""
        try:
            # Add academic context to the text
            academic_context = f"Academic excellence level: {excellence_tier}. "
            
            # Add tier-specific context
            tier_contexts = {
                'elite': "This content represents groundbreaking research and seminal work. ",
                'scholar': "This content demonstrates advanced scholarly analysis. ",
                'advanced': "This content shows sophisticated academic understanding. ",
                'basic': "This content covers fundamental academic concepts. "
            }
            
            contextualized_text = academic_context + tier_contexts.get(excellence_tier, "") + text
            
            response = self.client.embeddings.create(
                input=contextualized_text,
                model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        except Exception as e:
            self.logger.error(f"Excellence embedding generation failed: {str(e)}")
            # Return zero vector as fallback
            return [0.0] * 1536
    
    def _identify_scholarly_connections(self, text: str) -> Dict:
        """Identify scholarly connections and relationships in text"""
        connections = {
            'citations': [],
            'theories': [],
            'methodologies': [],
            'key_concepts': []
        }
        
        # Extract citations (basic pattern matching)
        citation_patterns = [
            r'\([A-Z][a-zA-Z\s]+,\s+\d{4}\)',  # (Author, 2023)
            r'\[[0-9,\s-]+\]',  # [1, 2, 3-5]
            r'[A-Z][a-zA-Z\s]+\s+et\s+al\.'   # Author et al.
        ]
        
        for pattern in citation_patterns:
            matches = re.findall(pattern, text)
            connections['citations'].extend(matches[:5])  # Limit to 5
        
        # Extract theories and frameworks
        theory_keywords = [
            'theory', 'framework', 'model', 'paradigm', 'approach'
        ]
        for keyword in theory_keywords:
            pattern = rf'\b\w+\s+{keyword}\b'
            matches = re.findall(pattern, text, re.IGNORECASE)
            connections['theories'].extend(matches[:3])
        
        # Extract methodologies
        method_keywords = [
            'analysis', 'method', 'technique', 'approach', 'procedure'
        ]
        for keyword in method_keywords:
            pattern = rf'\b\w+\s+{keyword}\b'
            matches = re.findall(pattern, text, re.IGNORECASE)
            connections['methodologies'].extend(matches[:3])
        
        # Extract key concepts (capitalized terms)
        concept_pattern = r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b'
        concepts = re.findall(concept_pattern, text)
        # Filter out common words and keep relevant concepts
        filtered_concepts = [c for c in concepts if len(c.split()) <= 3 and c not in ['The', 'This', 'That']]
        connections['key_concepts'] = filtered_concepts[:10]
        
        return connections
    
    def _calculate_complexity_score(self, text: str) -> float:
        """Calculate academic complexity score for text"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        if not words or not sentences:
            return 0.0
        
        # Basic metrics
        avg_word_length = sum(len(word) for word in words) / len(words)
        avg_sentence_length = len(words) / len(sentences)
        
        # Vocabulary sophistication (long words)
        sophisticated_words = sum(1 for word in words if len(word) > 8)
        sophistication_ratio = sophisticated_words / len(words)
        
        # Academic vocabulary
        academic_terms = [
            'analysis', 'methodology', 'framework', 'hypothesis', 'empirical',
            'theoretical', 'systematic', 'comprehensive', 'significant', 'correlation'
        ]
        academic_count = sum(1 for word in words 
                           if word.lower() in academic_terms)
        academic_ratio = academic_count / len(words)
        
        # Citation indicators
        citation_indicators = ['et al', 'ibid', 'op cit', 'cf.', 'viz.']
        citation_count = sum(1 for indicator in citation_indicators 
                           if indicator in text.lower())
        
        # Calculate final score (0-100)
        complexity_score = (
            avg_word_length * 8 +
            min(avg_sentence_length / 2, 20) +
            sophistication_ratio * 30 +
            academic_ratio * 25 +
            min(citation_count * 5, 15)
        )
        
        return min(complexity_score, 100.0)
    
    def _estimate_citation_potential(self, text: str) -> int:
        """Estimate potential citation count based on content quality"""
        words = text.split()
        
        # Quality indicators
        quality_indicators = [
            'novel', 'significant', 'important', 'crucial', 'essential',
            'groundbreaking', 'innovative', 'comprehensive', 'systematic'
        ]
        
        quality_score = sum(1 for word in words 
                          if word.lower() in quality_indicators)
        
        # Research indicators
        research_indicators = [
            'study', 'research', 'investigation', 'experiment', 'analysis'
        ]
        
        research_score = sum(1 for word in words 
                           if word.lower() in research_indicators)
        
        # Base citation potential
        base_citations = min(quality_score * 2 + research_score, 50)
        
        return base_citations
    
    def _calculate_impact_factor(self, text: str, excellence_tier: str) -> float:
        """Calculate potential impact factor based on tier and content"""
        # Base impact by tier
        tier_impacts = {
            'elite': 4.5,
            'scholar': 3.2,
            'advanced': 2.1,
            'basic': 0.8
        }
        
        base_impact = tier_impacts.get(excellence_tier, 1.0)
        
        # Adjust based on content characteristics
        complexity_score = self._calculate_complexity_score(text)
        complexity_factor = (complexity_score / 100) * 2
        
        # Innovation indicators
        innovation_keywords = [
            'novel', 'new', 'innovative', 'groundbreaking', 'first',
            'unique', 'original', 'unprecedented'
        ]
        
        innovation_count = sum(1 for keyword in innovation_keywords 
                             if keyword in text.lower())
        innovation_factor = min(innovation_count * 0.3, 1.5)
        
        final_impact = base_impact + complexity_factor + innovation_factor
        return min(final_impact, 10.0)
    
    def _store_document_chunks(self, processed_chunks: List[Dict]) -> List[int]:
        """Store processed chunks in database"""
        stored_ids = []
        
        for chunk in processed_chunks:
            try:
                query = """
                INSERT INTO academic_documents 
                (title, content, document_type, academic_level, excellence_tier, 
                 embedding, excellence_embedding, scholarly_connections, 
                 complexity_score, chunk_index, student_id, citation_count, 
                 impact_factor, processed_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                values = (
                    chunk['title'], chunk['content'], chunk['document_type'],
                    chunk['academic_level'], chunk['excellence_tier'],
                    chunk['embedding'], chunk['excellence_embedding'],
                    chunk['scholarly_connections'], chunk['complexity_score'],
                    chunk['chunk_index'], chunk['student_id'],
                    chunk['citation_count'], chunk['impact_factor'],
                    datetime.now()
                )
                
                result = self.db.execute_query(query, values)
                if result:
                    stored_ids.append(result.lastrowid if hasattr(result, 'lastrowid') else len(stored_ids))
                
            except Exception as e:
                self.logger.error(f"Failed to store chunk: {str(e)}")
                continue
        
        return stored_ids
    
    def _update_student_document_stats(self, student_id: str):
        """Update student's document processing statistics"""
        try:
            # Update document count and average complexity
            stats_query = """
            UPDATE scholar_profiles 
            SET document_count = (
                SELECT COUNT(DISTINCT title) 
                FROM academic_documents 
                WHERE student_id = %s
            ),
            avg_document_complexity = (
                SELECT AVG(complexity_score) 
                FROM academic_documents 
                WHERE student_id = %s
            ),
            last_document_processed = %s
            WHERE student_id = %s
            """
            
            self.db.execute_query(stats_query, (student_id, student_id, datetime.now(), student_id))
            
        except Exception as e:
            self.logger.error(f"Failed to update student stats: {str(e)}")
    
    def search_similar_documents(self, query_text: str, student_id: str = None, 
                                limit: int = 10) -> List[Dict]:
        """Search for similar documents using vector similarity"""
        try:
            # Generate embedding for query
            query_embedding = self._generate_standard_embedding(query_text)
            
            # Build search query
            base_query = """
            SELECT title, content, document_type, academic_level, excellence_tier,
                   complexity_score, citation_count, impact_factor,
                   VEC_COSINE_DISTANCE(embedding, %s) as similarity_score
            FROM academic_documents
            """
            
            params = [json.dumps(query_embedding)]
            
            if student_id:
                base_query += " WHERE student_id = %s"
                params.append(student_id)
            
            base_query += " ORDER BY similarity_score DESC LIMIT %s"
            params.append(limit)
            
            results = self.db.execute_query(base_query, params)
            
            return [{
                'title': row['title'],
                'content': row['content'][:500] + '...',  # Truncate content
                'document_type': row['document_type'],
                'academic_level': row['academic_level'],
                'excellence_tier': row['excellence_tier'],
                'complexity_score': float(row['complexity_score']),
                'citation_count': row['citation_count'],
                'impact_factor': float(row['impact_factor']),
                'similarity_score': float(row['similarity_score'])
            } for row in results]
            
        except Exception as e:
            self.logger.error(f"Document search failed: {str(e)}")
            return []
    
    def get_document_analytics(self, student_id: str) -> Dict:
        """Get analytics for student's processed documents"""
        try:
            analytics_query = """
            SELECT 
                COUNT(*) as total_documents,
                AVG(complexity_score) as avg_complexity,
                AVG(citation_count) as avg_citations,
                AVG(impact_factor) as avg_impact,
                excellence_tier,
                COUNT(*) as tier_count
            FROM academic_documents
            WHERE student_id = %s
            GROUP BY excellence_tier
            """
            
            results = self.db.execute_query(analytics_query, (student_id,))
            
            analytics = {
                'total_documents': 0,
                'avg_complexity': 0.0,
                'avg_citations': 0.0,
                'avg_impact': 0.0,
                'tier_distribution': {}
            }
            
            total_docs = 0
            weighted_complexity = 0
            weighted_citations = 0
            weighted_impact = 0
            
            for row in results:
                tier = row['excellence_tier']
                count = row['tier_count']
                
                analytics['tier_distribution'][tier] = count
                total_docs += count
                
                # Calculate weighted averages
                weighted_complexity += row['avg_complexity'] * count
                weighted_citations += row['avg_citations'] * count
                weighted_impact += row['avg_impact'] * count
            
            if total_docs > 0:
                analytics['total_documents'] = total_docs
                analytics['avg_complexity'] = weighted_complexity / total_docs
                analytics['avg_citations'] = weighted_citations / total_docs
                analytics['avg_impact'] = weighted_impact / total_docs
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Analytics generation failed: {str(e)}")
            return {
                'total_documents': 0,
                'avg_complexity': 0.0,
                'avg_citations': 0.0,
                'avg_impact': 0.0,
                'tier_distribution': {}
            }