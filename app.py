from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
import os
from datetime import datetime
from functools import wraps
from werkzeug.utils import secure_filename
import mimetypes
import sqlite3

# Import our enhanced models and configuration
from models import EnhancedKnowledgeBase, UserManager, EnhancedAIAssistant
from file_manager import FileManager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize components
file_manager = FileManager()
knowledge_base = EnhancedKnowledgeBase(file_manager)
user_manager = UserManager()
ai_assistant = EnhancedAIAssistant(knowledge_base, Config.GEMINI_API_KEY)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            return jsonify({'error': 'Admin icazəsi tələb olunur'}), 403
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')

        user = user_manager.authenticate(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['name'] = user['name']
            session['role'] = user['role']
            return jsonify({'success': True, 'user': user})
        else:
            return jsonify({'success': False, 'message': 'Yanlış istifadəçi adı və ya şifrə!'})

    return render_template('login.html')


@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    role = data.get('role')

    if user_manager.create_user(username, password, name, role):
        user = user_manager.authenticate(username, password)
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['name'] = user['name']
        session['role'] = user['role']
        return jsonify({'success': True, 'user': user})
    else:
        return jsonify({'success': False, 'message': 'Bu istifadəçi adı artıq mövcuddur!'})


@app.route('/dashboard')
@login_required
def dashboard():
    user_info = {
        'id': session['user_id'],
        'username': session['username'],
        'name': session['name'],
        'role': session['role']
    }

    # Get recent documents for dashboard
    recent_files = file_manager.list_files()[:5]  # Last 5 files

    return render_template('dashboard.html', user=user_info, recent_files=recent_files)


@app.route('/chat', methods=['POST'])
@login_required
def chat():
    try:
        data = request.json
        message = data.get('message', '').strip()

        if not message:
            return jsonify({'error': 'Boş mesaj göndərilə bilməz'}), 400

        user_info = {
            'id': session['user_id'],
            'username': session['username'],
            'name': session['name'],
            'role': session['role']
        }

        # Generate AI response with enhanced capabilities
        response = ai_assistant.generate_enhanced_response(message, user_info)

        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({
            'success': False,
            'error': 'Texniki problem yarandı. Zəhmət olmasa yenidən cəhd edin.'
        }), 500


@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """Handle file upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Fayl seçilməyib'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Fayl seçilməyib'}), 400

        # Get additional metadata
        category = request.form.get('category', 'Ümumi')
        description = request.form.get('description', '')
        tags = request.form.get('tags', '').split(',') if request.form.get('tags') else []

        # Save file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join('temp', filename)
        os.makedirs('temp', exist_ok=True)
        file.save(temp_path)

        # Process with file manager
        result = file_manager.upload_file(
            temp_path,
            category=category,
            tags=tags,
            description=description
        )

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        if result.get('success'):
            return jsonify({
                'success': True,
                'message': f'{filename} uğurla yükləndi',
                'file_info': result
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Fayl yüklənə bilmədi')
            }), 500

    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({
            'success': False,
            'error': 'Fayl yükləmə zamanı xəta baş verdi'
        }), 500


@app.route('/files')
@login_required
def list_files():
    """List all uploaded files"""
    try:
        category = request.args.get('category')
        files = file_manager.list_files(category=category)

        return jsonify({
            'success': True,
            'files': files
        })
    except Exception as e:
        print(f"List files error: {e}")
        return jsonify({
            'success': False,
            'error': 'Faylları yükləmə zamanı xəta baş verdi'
        }), 500


@app.route('/files/<file_id>')
@login_required
def get_file_content(file_id):
    """Get file content by ID"""
    try:
        chunk_index = request.args.get('chunk', type=int)
        content = file_manager.get_file_content(file_id, chunk_index)

        if content.get('error'):
            return jsonify({'error': content['error']}), 404

        return jsonify({
            'success': True,
            'content': content
        })
    except Exception as e:
        print(f"Get file error: {e}")
        return jsonify({
            'success': False,
            'error': 'Fayl məzmunu yüklənə bilmədi'
        }), 500


@app.route('/search-files')
@login_required
def search_files():
    """Search through uploaded files"""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category')

        if not query:
            return jsonify({'error': 'Axtarış sorğusu tələb olunur'}), 400

        results = file_manager.search_files(query, category=category)

        return jsonify({
            'success': True,
            'results': results,
            'query': query
        })
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({
            'success': False,
            'error': 'Axtarış zamanı xəta baş verdi'
        }), 500


@app.route('/bulk-upload', methods=['POST'])
@admin_required
def bulk_upload():
    """Bulk upload files from directory (Admin only)"""
    try:
        data = request.json
        directory_path = data.get('directory_path')
        category = data.get('category', 'Bulk Upload')

        if not directory_path:
            return jsonify({'error': 'Directory path tələb olunur'}), 400

        if not os.path.exists(directory_path):
            return jsonify({'error': 'Directory tapılmadı'}), 400

        result = file_manager.bulk_upload(directory_path, category=category)

        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        print(f"Bulk upload error: {e}")
        return jsonify({
            'success': False,
            'error': 'Bulk upload zamanı xəta baş verdi'
        }), 500


@app.route('/file-stats')
@login_required
def file_stats():
    """Get file statistics"""
    try:
        files = file_manager.list_files()

        stats = {
            'total_files': len(files),
            'file_types': {},
            'categories': {},
            'total_size': 0
        }

        for file_info in files:
            # Count by file type
            file_type = file_info['file_type']
            stats['file_types'][file_type] = stats['file_types'].get(file_type, 0) + 1

            # Count by category
            category = file_info.get('category', 'Uncategorized')
            stats['categories'][category] = stats['categories'].get(category, 0) + 1

            # Sum file sizes
            stats['total_size'] += file_info.get('file_size', 0)

        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({
            'success': False,
            'error': 'Statistikalar yüklənə bilmədi'
        }), 500


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/api/knowledge-search')
@login_required
def knowledge_search():
    """Enhanced knowledge search including documents"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'Axtarış sorğusu tələb olunur'}), 400

        results = knowledge_base.search(query)

        return jsonify({
            'success': True,
            'results': results,
            'query': query
        })
    except Exception as e:
        print(f"Knowledge search error: {e}")
        return jsonify({
            'success': False,
            'error': 'Bilik bazası axtarışında xəta baş verdi'
        }), 500


@app.route('/documents')
@login_required
def documents_page():
    """Documents management page"""
    user_info = {
        'id': session['user_id'],
        'username': session['username'],
        'name': session['name'],
        'role': session['role']
    }
    return render_template('documents.html', user=user_info)


# Add these routes to your existing app.py file

@app.route('/download/<file_id>')
@login_required
def download_file(file_id):
    """Download a file by its ID"""
    try:
        # Get file info from database
        conn = sqlite3.connect(file_manager.db_path)
        cursor = conn.cursor()
        cursor.execute('''
                       SELECT filename, file_path, file_type
                       FROM files
                       WHERE id = ?
                       ''', (file_id,))

        file_info = cursor.fetchone()
        conn.close()

        if not file_info:
            return jsonify({'error': 'File not found'}), 404

        filename, file_path, file_type = file_info

        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({'error': 'Physical file not found'}), 404

        # Send file
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetypes.guess_type(filename)[0]
        )

    except Exception as e:
        print(f"Download error: {e}")
        return jsonify({'error': 'Download failed'}), 500


@app.route('/download-all')
@admin_required
def download_all_files():
    """Download all files as ZIP (Admin only)"""
    try:
        import zipfile
        from io import BytesIO

        # Create ZIP in memory
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Get all files
            files = file_manager.list_files()

            for file_info in files:
                file_path = None

                # Get file path from database
                conn = sqlite3.connect(file_manager.db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT file_path FROM files WHERE id = ?', (file_info['file_id'],))
                result = cursor.fetchone()
                conn.close()

                if result and os.path.exists(result[0]):
                    file_path = result[0]
                    # Add file to ZIP with category folder structure
                    category = file_info.get('category', 'Uncategorized')
                    zip_path = f"{category}/{file_info['filename']}"
                    zip_file.write(file_path, zip_path)

        zip_buffer.seek(0)

        return send_file(
            BytesIO(zip_buffer.read()),
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'nazirlik_documents_{datetime.now().strftime("%Y%m%d")}.zip'
        )

    except Exception as e:
        print(f"Download all error: {e}")
        return jsonify({'error': 'ZIP creation failed'}), 500


@app.route('/files/<file_id>/info')
@login_required
def get_file_info(file_id):
    """Get detailed file information"""
    try:
        conn = sqlite3.connect(file_manager.db_path)
        cursor = conn.cursor()

        cursor.execute('''
                       SELECT f.*, COUNT(c.id) as chunk_count
                       FROM files f
                                LEFT JOIN chunks c ON f.id = c.file_id
                       WHERE f.id = ?
                       GROUP BY f.id
                       ''', (file_id,))

        file_data = cursor.fetchone()
        conn.close()

        if not file_data:
            return jsonify({'error': 'File not found'}), 404

        file_info = {
            'file_id': file_data[0],
            'filename': file_data[1],
            'original_name': file_data[2],
            'file_type': file_data[4],
            'file_size': file_data[5],
            'upload_date': file_data[7],
            'category': file_data[9],
            'description': file_data[11],
            'chunk_count': file_data[14],
            'download_url': url_for('download_file', file_id=file_id)
        }

        return jsonify({
            'success': True,
            'file_info': file_info
        })

    except Exception as e:
        print(f"File info error: {e}")
        return jsonify({'error': 'Could not get file info'}), 500


@app.route('/export-data')
@admin_required
def export_data():
    """Export all data including files and database (Admin only)"""
    try:
        import zipfile
        from io import BytesIO
        import json

        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:

            # 1. Add all documents
            files = file_manager.list_files()
            for file_info in files:
                conn = sqlite3.connect(file_manager.db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT file_path FROM files WHERE id = ?', (file_info['file_id'],))
                result = cursor.fetchone()
                conn.close()

                if result and os.path.exists(result[0]):
                    category = file_info.get('category', 'Uncategorized')
                    zip_path = f"documents/{category}/{file_info['filename']}"
                    zip_file.write(result[0], zip_path)

            # 2. Add databases
            if os.path.exists('users.db'):
                zip_file.write('users.db', 'database/users.db')
            if os.path.exists('file_index.db'):
                zip_file.write('file_index.db', 'database/file_index.db')

            # 3. Add file metadata as JSON
            metadata = {
                'export_date': datetime.now().isoformat(),
                'total_files': len(files),
                'files': files
            }
            zip_file.writestr('metadata.json', json.dumps(metadata, ensure_ascii=False, indent=2))

        zip_buffer.seek(0)

        return send_file(
            BytesIO(zip_buffer.read()),
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'nazirlik_full_export_{datetime.now().strftime("%Y%m%d_%H%M")}.zip'
        )

    except Exception as e:
        print(f"Export error: {e}")
        return jsonify({'error': 'Export failed'}), 500

@app.route('/files-manager')
@login_required
def files_manager():
    """File management page"""
    user_info = {
        'id': session['user_id'],
        'username': session['username'],
        'name': session['name'],
        'role': session['role']
    }
    return render_template('files.html', user=user_info)

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(Config.TEMPLATES_DIR, exist_ok=True)
    os.makedirs('temp', exist_ok=True)
    os.makedirs('documents', exist_ok=True)

    print("🚀 Enhanced AI Onboarding System Starting...")
    print("📧 Demo Accounts:")
    print("   Admin: admin / admin123")
    print("   Minister: nazir / nazir123")
    print("   Analyst: analitik / data123")
    print("🤖 Gemini 2.5 Flash AI Model: Ready")
    print("📁 File Management System: Ready")
    print("🔍 Document Search: Ready")
    print(f"🌐 Server: http://{Config.HOST}:{Config.PORT}")

    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)