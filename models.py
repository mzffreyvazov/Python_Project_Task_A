import google.generativeai as genai
import json
import sqlite3
import hashlib
from datetime import datetime
from file_manager import FileManager
import logging

logger = logging.getLogger(__name__)


class EnhancedKnowledgeBase:
    """Enhanced knowledge base that integrates with file management system"""

    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager
        self.static_data = {
            "structure": {
                "nazirlik": "Nazirlik aşağıdakı əsas şöbələrdən ibarətdir: İdarəetmə Şöbəsi, Maliyyə Şöbəsi, İnsan Resursları, Texniki Dəstək və Layihə İdarəetməsi.",
                "şöbələr": "Bizim nazirlikdə 5 əsas şöbə var: İdarəetmə (20 nəfər), Maliyyə (15 nəfər), İnsan Resursları (8 nəfər), Texniki Dəstək (12 nəfər), Layihə İdarəetməsi (25 nəfər).",
                "struktur": "İdarəetmə Şöbəsi - Kamran Məmmədov, Maliyyə Şöbəsi - Səməd Əliyev, İnsan Resursları - Günel Məmmədova, Texniki Dəstək - Elvin Qasımov, Layihə İdarəetməsi - Rəşad Həsənov"
            },
            "contacts": {
                "maliyyə": "Maliyyə şöbəsi üçün əlaqə: Rəhbər - Səməd Əliyev (samad.aliyev@nazirlik.gov.az, +994-12-555-0101)",
                "hr": "İnsan Resursları üçün əlaqə: Rəhbər - Günel Məmmədova (gunel.mammadova@nazirlik.gov.az, +994-12-555-0102)",
                "texniki": "Texniki Dəstək üçün əlaqə: Rəhbər - Elvin Qasımov (elvin.qasimov@nazirlik.gov.az, +994-12-555-0103)",
                "idarəetmə": "İdarəetmə Şöbəsi üçün əlaqə: Rəhbər - Kamran Məmmədov (kamran.mammadov@nazirlik.gov.az, +994-12-555-0100)",
                "layihə": "Layihə İdarəetməsi üçün əlaqə: Rəhbər - Rəşad Həsənov (rashad.hasanov@nazirlik.gov.az, +994-12-555-0104)"
            },
            "documents": {
                "məzuniyyət": "Məzuniyyət ərizəsi nümunəsi: TARİX, AD SOYAD, VƏZİFƏ, məzuniyyət növü və müddəti qeyd edilməlidir. HR şöbəsi ilə əlaqə: gunel.mammadova@nazirlik.gov.az",
                "ezamiyyə": "Ezamiyyə ərizəsi nümunəsi: Ezamiyyə yeri, müddəti, məqsədi və xərc hesablaması daxil edilməlidir. Günlük yemək pulu 25 AZN, yaşayış 50 AZN.",
                "arayış": "Arayış şablonu: Standart arayış formatı ilə hazırlanmalıdır. HR şöbəsi tərəfindən verilir.",
                "ərizə": "Bütün ərizə növləri üçün HR şöbəsi ilə əlaqə saxlayın: +994-12-555-0102"
            },
            "regulations": {
                "məzuniyyət_günləri": "İllik məzuniyyət hüququ: 21 iş günü əsas məzuniyyət + əlavə məzuniyyətlər (10+ il staj üçün əlavə 3 gün).",
                "maliyyə_hesablama": "Ezamiyyə xərcləri: günlük yemək pulu 25 AZN, yaşayış 50 AZN, nəqliyyat faktiki xərc üzrə hesablanır.",
                "işə_qəbul": "Yeni işçi qəbulu proseduru: CV təqdimi → müayinə → sənəd təhvili → təlim proqramı → trial period 3 ay.",
                "iş_saatları": "İş saatları: 09:00-18:00, nahar fasiləsi: 13:00-14:00",
                "xəstəlik": "Xəstəlik məzuniyyəti üçün həkim arayışı tələb olunur. 3 gündən çox olan hallarda rəsmi arayış məcburidir."
            },
            "projects": {
                "rəqəmsal_həkimlik": {
                    "status": "Development fazasında (75% hazır)",
                    "contact": "Layihə rəhbəri: Dr. Zaur Əhmədov (zaur.ahmadov@nazirlik.gov.az, +994-12-555-0201)",
                    "lastUpdate": "2024-12-15",
                    "document": "Rəqəmsal_Həkimlik_Layihəsi_v2.3.pdf",
                    "deadline": "2025-ci il mart ayı"
                },
                "smart_city": {
                    "status": "Pilot test fazasında (60% hazır)",
                    "contact": "Layihə rəhbəri: Nigar Həsənova (nigar.hasanova@nazirlik.gov.az, +994-12-555-0202)",
                    "lastUpdate": "2024-12-20",
                    "document": "Smart_City_Implementation_v1.8.pdf",
                    "test_area": "Yasamal rayonu"
                },
                "e_governance": {
                    "status": "İnisial fazada (25% hazır)",
                    "contact": "Layihə rəhbəri: Tural Əliyev (tural.aliyev@nazirlik.gov.az, +994-12-555-0203)",
                    "lastUpdate": "2024-12-10",
                    "document": "E_Governance_Proposal_v1.2.pdf",
                    "start_date": "2025-ci il yanvar"
                }
            },
            "templates": {
                "məzuniyyət_ərizəsi": """TARİX: [Tarix]
KÖMÜNƏ: [Şöbə rəhbəri]
KİMDƏN: [Ad Soyad, Vəzifə]

Məzuniyyət ərizəsi

Hörmətli [Rəhbər adı],

[Başlama tarixi] - [Bitmə tarixi] tarixləri arasında [gün sayı] gün illik məzuniyyətə çıxmaq üçün icazə verilməsini xahiş edirəm.

Hörmətlə,
[Ad Soyad]""",

                "ezamiyyə_ərizəsi": """TARİX: [Tarix]
KÖMÜNƏ: [Şöbə rəhbəri]
KİMDƏN: [Ad Soyad, Vəzifə]

Ezamiyyə ərizəsi

Hörmətli [Rəhbər adı],

[Başlama tarixi] - [Bitmə tarixi] tarixləri arasında [şəhər/ölkə] şəhərinə iş ezamiyyətinə göndərilməyimi xahiş edirəm.

Ezamiyyənin məqsədi: [Məqsəd]
Təxmini xərc: [Məbləğ] AZN

Hörmətlə,
[Ad Soyad]"""
            }
        }

    def search_static_data(self, query: str) -> str:
        """Search through static knowledge base"""
        query_lower = query.lower()
        relevant_info = []

        for category, items in self.static_data.items():
            for key, value in items.items():
                if any(term in key.lower() or term in str(value).lower()
                       for term in query_lower.split()):
                    if isinstance(value, dict):
                        relevant_info.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
                    else:
                        relevant_info.append(f"{key}: {value}")

        return "\n".join(relevant_info) if relevant_info else ""

    def search_documents(self, query: str, max_results: int = 5) -> str:
        """Search through uploaded documents"""
        try:
            search_results = self.file_manager.search_files(query)
            if not search_results:
                return ""

            document_info = []
            for i, result in enumerate(search_results[:max_results]):
                # Get relevant content from the document
                file_content = self.file_manager.get_file_content(result['file_id'])

                doc_info = f"""
Sənəd: {result['filename']} (Növ: {result['file_type']})
Kateqoriya: {result.get('category', 'Təyin edilməyib')}
Təsvir: {result.get('description', 'Təsvir yoxdur')}
Əlaqəli məzmun: {result.get('snippet', file_content.get('content', '')[:300])}...
"""
                document_info.append(doc_info)

            return "\n".join(document_info)
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return ""

    def search(self, query: str) -> str:
        """Enhanced search that combines static data and document search"""
        # Search static data
        static_results = self.search_static_data(query)

        # Search documents
        document_results = self.search_documents(query)

        # Combine results
        all_results = []
        if static_results:
            all_results.append("=== ƏSAS MƏLUMATLAR ===")
            all_results.append(static_results)

        if document_results:
            all_results.append("\n=== SƏNƏDLƏR ===")
            all_results.append(document_results)

        return "\n".join(all_results) if all_results else "Heç bir məlumat tapılmadı."

    def get_document_by_name(self, filename: str) -> dict:
        """Get specific document by filename"""
        try:
            files = self.file_manager.list_files()
            for file_info in files:
                if filename.lower() in file_info['filename'].lower():
                    return self.file_manager.get_file_content(file_info['file_id'])
            return {'error': 'Sənəd tapılmadı'}
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return {'error': str(e)}


class UserManager:
    """User management remains the same"""

    def __init__(self):
        self.init_db()
        self.add_demo_users()

    def init_db(self):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS users
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           username
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           password_hash
                           TEXT
                           NOT
                           NULL,
                           name
                           TEXT
                           NOT
                           NULL,
                           role
                           TEXT
                           NOT
                           NULL,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')
        conn.commit()
        conn.close()

    def add_demo_users(self):
        demo_users = [
            ('admin', 'admin123', 'Sistem Administratoru', 'admin'),
            ('nazir', 'nazir123', 'Əli Məmmədov', 'minister'),
            ('analitik', 'data123', 'Leyla Həsənova', 'analyst')
        ]

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        for username, password, name, role in demo_users:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute('''
                           INSERT
                           OR IGNORE INTO users (username, password_hash, name, role)
                VALUES (?, ?, ?, ?)
                           ''', (username, password_hash, name, role))

        conn.commit()
        conn.close()

    def authenticate(self, username, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
                       SELECT id, username, name, role
                       FROM users
                       WHERE username = ?
                         AND password_hash = ?
                       ''', (username, password_hash))
        user = cursor.fetchone()
        conn.close()

        if user:
            return {
                'id': user[0],
                'username': user[1],
                'name': user[2],
                'role': user[3]
            }
        return None

    def create_user(self, username, password, name, role):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        try:
            cursor.execute('''
                           INSERT INTO users (username, password_hash, name, role)
                           VALUES (?, ?, ?, ?)
                           ''', (username, password_hash, name, role))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()


class EnhancedAIAssistant:
    """Enhanced AI Assistant with better document handling and context management"""

    def __init__(self, knowledge_base: EnhancedKnowledgeBase, gemini_api_key: str):
        self.kb = knowledge_base
        # Configure Gemini API
        genai.configure(api_key=gemini_api_key)
        # Initialize Gemini model
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.conversation_history = {}  # Store conversation context per user

    def get_role_context(self, role: str) -> str:
        contexts = {
            'admin': 'Admin olaraq bütün sistemlərə və məlumatlara girişin var. Bütün sualları cavablandıra bilərsən. Həmçinin sənəd yükləmə və idarəetmə hüququn var.',
            'minister': 'Nazirlik rəhbəri olaraq dashboard, layihə statusları və ümumi məlumat əldə edə bilərsən. Bütün sənədlərə baxış hüququn var.',
            'analyst': 'Data analitik olaraq əsasən data yükləmə, təhlil və insight məlumatları əldə edə bilərsən. Sənəd axtarışı və təhlili edə bilərsən.'
        }
        return contexts.get(role, '')

    def get_role_display_name(self, role: str) -> str:
        role_names = {
            'admin': 'Admin',
            'minister': 'Nazirlik işçisi / rəhbər şəxs',
            'analyst': 'Data yükləyici / analitik'
        }
        return role_names.get(role, role)

    def maintain_conversation_context(self, user_id: str, message: str, response: str):
        """Maintain conversation context for better follow-up questions"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []

        self.conversation_history[user_id].append({
            'user_message': message,
            'ai_response': response,
            'timestamp': datetime.now().isoformat()
        })

        # Keep only last 5 interactions to manage memory
        if len(self.conversation_history[user_id]) > 5:
            self.conversation_history[user_id] = self.conversation_history[user_id][-5:]

    def get_conversation_context(self, user_id: str) -> str:
        """Get recent conversation context"""
        if user_id not in self.conversation_history:
            return ""

        context_parts = []
        for interaction in self.conversation_history[user_id][-3:]:  # Last 3 interactions
            context_parts.append(f"İstifadəçi: {interaction['user_message']}")
            context_parts.append(f"AI: {interaction['ai_response'][:200]}...")

        return "\n".join(context_parts) if context_parts else ""

    def detect_document_request(self, message: str) -> dict:
        """Detect if user is asking for a specific document"""
        document_keywords = {
            'sənəd': 'document',
            'fayl': 'file',
            'pdf': 'pdf',
            'ərizə': 'application',
            'nümunə': 'template',
            'şablon': 'template',
            'layihə': 'project',
            'hesabat': 'report',
            'təlimat': 'instruction'
        }

        message_lower = message.lower()
        detected_types = []

        for keyword, doc_type in document_keywords.items():
            if keyword in message_lower:
                detected_types.append(doc_type)

        return {
            'has_document_request': len(detected_types) > 0,
            'document_types': detected_types,
            'specific_filename': self.extract_filename_from_message(message)
        }

    def extract_filename_from_message(self, message: str) -> str:
        """Try to extract specific filename from user message"""
        # Look for common file extensions
        import re
        pattern = r'([a-zA-Z0-9_-]+\.(pdf|docx|xlsx|txt|md))'
        match = re.search(pattern, message, re.IGNORECASE)
        return match.group(1) if match else ""

    def generate_enhanced_response(self, user_message: str, user_info: dict) -> str:
        """Enhanced response generation with better context and document handling"""
        try:
            user_id = str(user_info['id'])

            # Get conversation context
            conversation_context = self.get_conversation_context(user_id)

            # Detect document requests
            doc_request = self.detect_document_request(user_message)

            # Get context information from knowledge base
            role_context = self.get_role_context(user_info['role'])
            context_info = self.kb.search(user_message)

            # Handle specific document requests
            document_content = ""
            if doc_request['has_document_request'] and doc_request['specific_filename']:
                doc_result = self.kb.get_document_by_name(doc_request['specific_filename'])
                if not doc_result.get('error'):
                    document_content = f"\n=== XÜSUSI SƏNƏD MƏZMUNU ===\n{doc_result.get('content', '')[:2000]}..."

            # Create enhanced prompt with better structure
            system_prompt = f"""
Sən Azərbaycan Respublikası nazirlik işçiləri üçün AI onboarding asistantısan.

👤 İSTİFADƏÇİ MƏLUMATLARI:
- Ad: {user_info['name']}
- Rol: {self.get_role_display_name(user_info['role'])}
- İstifadəçi adı: {user_info['username']}

🎯 ROL ƏSASLI İCAZƏLƏR:
{role_context}

💬 SON DANIŞIQLAR:
{conversation_context}

📚 KONTEKST MƏLUMATLARI:
{context_info}

{document_content}

❓ YENİ SUAL: "{user_message}"

📋 CAVAB QAYDLARI:
1. YALNIZ Azərbaycan dilində cavab ver
2. Rəsmi lakin dostcasına ton istifadə et
3. Əgər konkret sənəd və ya əlaqə məlumatı varsa, mutləq qeyd et
4. Əgər məlumat yoxdursa, hansı şəxslə əlaqə saxlamaq lazım olduğunu bildir
5. Layihə statusu soruşulursa, həm son statusu həm də son sənədi qeyd et
6. Sənəd nümunəsi istənilsə, tam şablonu göstər
7. Böyük sənədlərdən məlumat istənilsə, əsas nöqtələri ümumiləşdir
8. Əlaqə məlumatlarını (email və telefon) daxil et
9. Əgər əvvəlki sualla əlaqəli follow-up sualıdırsa, konteksti nəzərə al
10. Sənəd axtarışı tələb olunursa, uyğun fayl adlarını təklif et

CAVAB (2-6 cümlə):"""

            # Generate response using Gemini
            response = self.model.generate_content(
                system_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    top_k=40,
                    top_p=0.95,
                    max_output_tokens=1024,
                )
            )

            response_text = response.text

            # Maintain conversation context
            self.maintain_conversation_context(user_id, user_message, response_text)

            return response_text

        except Exception as e:
            logger.error(f"AI Error: {e}")
            return "Üzr istəyirəm, hazırda texniki problem var. Zəhmət olmasa sonra yenidən cəhd edin."

    def generate_response(self, user_message: str, user_info: dict) -> str:
        """Wrapper method for backward compatibility"""
        return self.generate_enhanced_response(user_message, user_info)

    def get_available_documents(self, category: str = None) -> list:
        """Get list of available documents for user reference"""
        try:
            return self.kb.file_manager.list_files(category=category)
        except Exception as e:
            logger.error(f"Error getting documents: {e}")
            return []

    def search_documents_for_user(self, query: str, user_role: str) -> list:
        """Search documents with role-based filtering if needed"""
        try:
            results = self.kb.file_manager.search_files(query)

            # Future: Add role-based filtering here if needed
            # For now, return all results but could filter based on user_role

            return results
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []