"""
Rutas de API (JSON endpoints)
"""
from flask import Blueprint, send_file, request, jsonify
from io import BytesIO
from collections import OrderedDict
from pathlib import Path
import time
import requests
from urllib.parse import quote
from config import OCI_PREAUTH_URL_READ
from controllers.test_controller import TestController
from controllers.advisory_controller import AdvisoryController
from controllers.career_controller import CareerController
from controllers.auth_controller import AuthController
from controllers.predictions_controller import PredictionsController
from controllers.visits_controller import VisitsController
from controllers.upload_controller import UploadController
from controllers.nps_controller import NpsController

api_bp = Blueprint('api', __name__, url_prefix='/api')

IMAGE_PROXY_CACHE_TTL_SECONDS = 3600
IMAGE_PROXY_CACHE_MAX_ITEMS = 256
image_proxy_cache = OrderedDict()


def _load_image_maps():
    """Cargar mapas de nombres y URLs desde archivo generado de URLs."""
    current_file = Path(__file__).resolve()
    project_root = current_file.parents[2]
    map_path = project_root / 'frontend' / 'static' / 'images' / 'oci_read_urls.txt'

    if not map_path.exists():
        return {}, {}

    name_map = {}
    url_map = {}
    try:
        for line in map_path.read_text(encoding='utf-8').splitlines():
            if '\t' not in line:
                continue
            file_name, file_url = line.split('\t', 1)
            normalized = file_name.casefold().strip()
            if normalized:
                name_map[normalized] = file_name
                url_map[file_name] = file_url.strip()
    except Exception:
        return {}, {}

    return name_map, url_map


image_name_map, image_url_map = _load_image_maps()


# Auth endpoints
api_bp.add_url_rule('/auth/register', 'register', 
                    AuthController.register, methods=['POST'])
api_bp.add_url_rule('/auth/login', 'login',
                    AuthController.login, methods=['POST'])
api_bp.add_url_rule('/auth/profile', 'get_profile',
                    AuthController.get_profile, methods=['GET'])
api_bp.add_url_rule('/auth/check-session', 'check_session',
                    AuthController.check_session, methods=['GET'])
api_bp.add_url_rule('/auth/logout', 'logout',
                    AuthController.logout, methods=['POST'])

# Test endpoints
api_bp.add_url_rule('/test-submit', 'submit_test', 
                    TestController.submit_test, methods=['POST'])

api_bp.add_url_rule('/test-questions', 'get_test_questions',
                    TestController.get_afirmaciones_controller, methods=['GET'])

api_bp.add_url_rule('/test-status', 'get_test_status',
                    TestController.get_test_status, methods=['GET'])

api_bp.add_url_rule('/reset-test', 'reset_test',
                    TestController.reset_test, methods=['POST'])

api_bp.add_url_rule('/save-answers', 'save_answers',
                    TestController.save_answers, methods=['POST'])

# Predictions endpoints
api_bp.add_url_rule('/predict-careers', 'predict_careers',
                    PredictionsController.predict_careers, methods=['POST'])
api_bp.add_url_rule('/occupations', 'get_occupations',
                    PredictionsController.get_occupations, methods=['GET'])

# Advisory endpoints
api_bp.add_url_rule('/advisors', 'get_advisors',
                    AdvisoryController.get_advisors, methods=['GET'])
api_bp.add_url_rule('/advisory-submit', 'book_advisory',
                    AdvisoryController.book_advisory, methods=['POST'])
api_bp.add_url_rule('/available-times', 'get_available_times',
                    AdvisoryController.get_available_times, methods=['GET'])
api_bp.add_url_rule('/booked-slots', 'get_booked_slots',
                    AdvisoryController.get_booked_slots, methods=['GET'])
api_bp.add_url_rule('/advisory/my-bookings', 'get_my_bookings',
                    AdvisoryController.get_my_bookings, methods=['GET'])
api_bp.add_url_rule('/advisory/<int:booking_id>', 'cancel_booking',
                    AdvisoryController.cancel_booking, methods=['DELETE'])

# Career endpoints
api_bp.add_url_rule('/careers/list', 'get_careers_list',
                    CareerController.get_careers_list, methods=['GET'])
api_bp.add_url_rule('/careers/all', 'get_all_careers_full',
                    CareerController.get_all_careers_full, methods=['GET'])
api_bp.add_url_rule('/careers/<int:career_id>/detail', 'get_career_detail',
                    CareerController.get_career_detail, methods=['GET'])
api_bp.add_url_rule('/careers', 'get_all_careers',
                    CareerController.get_all_careers, methods=['GET'])
api_bp.add_url_rule('/careers/<int:career_id>', 'get_career',
                    CareerController.get_career, methods=['GET'])
api_bp.add_url_rule('/careers/clear-cache', 'clear_careers_cache',
                    CareerController.clear_cache, methods=['POST'])

# Visits endpoints (para rastrear visitantes anónimos)
api_bp.add_url_rule('/visits/register', 'register_visit',
                    VisitsController.register_visit, methods=['POST'])
api_bp.add_url_rule('/visits/info', 'get_visitor_info',
                    VisitsController.get_visitor_info, methods=['GET'])
api_bp.add_url_rule('/visits/statistics', 'get_visit_statistics',
                    VisitsController.get_statistics, methods=['GET'])

# Upload endpoints (subida de imágenes a OCI)
api_bp.add_url_rule('/upload/image', 'upload_image',
                    UploadController.upload_image, methods=['POST'])
api_bp.add_url_rule('/upload/images', 'upload_multiple_images',
                    UploadController.upload_multiple_images, methods=['POST'])

# NPS endpoints
api_bp.add_url_rule('/nps/check', 'nps_check',
                    NpsController.check_eligibility, methods=['GET'])
api_bp.add_url_rule('/nps/update-time', 'nps_update_time',
                    NpsController.update_time, methods=['POST'])
api_bp.add_url_rule('/nps/submit', 'nps_submit',
                    NpsController.submit_response, methods=['POST'])
api_bp.add_url_rule('/nps/status', 'nps_status',
                    NpsController.get_status, methods=['GET'])


# Image proxy endpoint (sirve imágenes desde OCI sin problemas CORS)
@api_bp.route('/image/proxy', methods=['GET'])
def proxy_image():
    """
    Proxy para servir imágenes desde OCI Object Storage
    Soluciona problemas de CORS descargando en backend y reenviando
    
    Parámetro: path = ruta relativa (ej: 'ikigais_images/Administración de Empresas.svg')
    Uso: GET /api/image/proxy?path=ikigais_images/logo.svg
    """
    try:
        # Obtener ruta desde parámetro
        image_path = request.args.get('path', '')
        
        if not image_path:
            return jsonify({'error': 'Falta parámetro "path"'}), 400
        
        # Intentar primero con la ruta recibida y luego con fallback al nombre de archivo
        candidate_paths = [image_path]
        if '/' in image_path:
            candidate_paths.append(image_path.rsplit('/', 1)[-1])

        # Resolver diferencias de mayúsculas/minúsculas con mapa local de nombres
        last_segment = candidate_paths[-1]
        mapped_name = image_name_map.get(last_segment.casefold().strip())
        if mapped_name and mapped_name not in candidate_paths:
            candidate_paths.append(mapped_name)

        now = time.time()

        # 1) Buscar primero en cache de proxy
        for candidate in candidate_paths:
            cached_item = image_proxy_cache.get(candidate)
            if not cached_item:
                continue

            if cached_item['expires_at'] <= now:
                image_proxy_cache.pop(candidate, None)
                continue

            image_proxy_cache.move_to_end(candidate)
            response_obj = send_file(
                BytesIO(cached_item['content']),
                mimetype=cached_item['content_type'],
                as_attachment=False
            )
            response_obj.headers['Cache-Control'] = f'public, max-age={IMAGE_PROXY_CACHE_TTL_SECONDS}'
            return response_obj

        # 2) Si no existe en cache, descargar desde OCI
        image_bytes = None
        content_type = None
        final_path = None

        for candidate in candidate_paths:
            candidate_urls = []
            mapped_url = image_url_map.get(candidate)
            if mapped_url:
                candidate_urls.append(mapped_url)

            if OCI_PREAUTH_URL_READ:
                encoded_path = quote(candidate, safe='/')
                candidate_urls.append(OCI_PREAUTH_URL_READ + encoded_path)

            for oci_url in candidate_urls:
                try:
                    current_response = requests.get(oci_url, timeout=10)
                except requests.exceptions.RequestException:
                    continue

                if current_response.status_code == 200:
                    image_bytes = current_response.content
                    response_type = current_response.headers.get('Content-Type', '')
                    content_type = response_type.split(';')[0] if response_type else None
                    final_path = candidate
                    break

            if image_bytes is not None:
                break

        if image_bytes is None:
            return jsonify({'error': 'Error descargando imagen: 404'}), 404

        # Determinar tipo MIME basado en extensión (fallback)
        if not content_type:
            content_type = 'image/svg+xml' if final_path.lower().endswith('.svg') else 'image/png'
        if final_path.lower().endswith('.jpg') or final_path.lower().endswith('.jpeg'):
            content_type = 'image/jpeg'
        elif final_path.lower().endswith('.gif'):
            content_type = 'image/gif'

        # Guardar en cache en memoria
        image_proxy_cache[final_path] = {
            'content': image_bytes,
            'content_type': content_type,
            'expires_at': now + IMAGE_PROXY_CACHE_TTL_SECONDS
        }
        image_proxy_cache.move_to_end(final_path)

        while len(image_proxy_cache) > IMAGE_PROXY_CACHE_MAX_ITEMS:
            image_proxy_cache.popitem(last=False)
        
        # Devolver imagen con headers CORS
        response_obj = send_file(
            BytesIO(image_bytes),
            mimetype=content_type,
            as_attachment=False
        )
        response_obj.headers['Cache-Control'] = f'public, max-age={IMAGE_PROXY_CACHE_TTL_SECONDS}'
        return response_obj
    
    except Exception as e:
        print(f"Error en proxy de imagen: {e}")
        return jsonify({'error': str(e)}), 500

#ci/cd