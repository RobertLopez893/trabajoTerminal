import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from backend.api import parents
from backend.database.models import Usuario
from backend.database.models_auditoria import LogAuditoria, AlertaUsuario
from backend.database.schemas import ParentVerifyCodeRequest
from backend.api.jwt_manager import verify_access_token
from security.aes.aes_gcm import AESGCMCipher


class TestParentAPIUnit(unittest.TestCase):

    def setUp(self):
        self.aes = AESGCMCipher()
        self.test_phone = "5512345678"
        enc_phone = self.aes.encrypt(self.test_phone)

        self.mock_user = Usuario(
            id="mock-child-uuid-1234",
            nickname="ExploradorLunar",
            telefono_cifrado=enc_phone["ciphertext_b64"],
            telefono_iv_nonce=enc_phone["nonce_b64"],
            telefono_tag=enc_phone["tag_b64"],
            argon2id_hash="dummy_hash",
            salt="dummy_salt",
            is_verified=True,
            is_active=True,
            is_banned=False
        )

    def test_request_code_success(self):
        with patch("backend.api.parents.send_verification_sms", return_value=True):
            res = parents.request_parent_verification_code(current_user=self.mock_user)
            self.assertEqual(res.status, "success")
            self.assertIn("78", res.masked_phone)
            self.assertEqual(res.expires_in_seconds, 120)

    def test_verify_code_fallback_and_token_generation(self):
        req = ParentVerifyCodeRequest(codigo="123456")
        res = parents.verify_parent_code(req=req, current_user=self.mock_user)
        self.assertEqual(res.status, "success")
        self.assertIsNotNone(res.parent_token)

        payload = verify_access_token(res.parent_token)
        self.assertEqual(payload["role"], "parent")
        self.assertEqual(payload["sub"], self.mock_user.id)
        self.assertEqual(payload["nickname"], "ExploradorLunar")

    def test_dashboard_with_alerts(self):
        mock_db_audit = MagicMock()
        mock_alerta = AlertaUsuario(
            id=10,
            usuario_receptor_id_ref=self.mock_user.id,
            usuario_victima_id_ref=self.mock_user.id,
            log_id_ref=1,
            estado="ENVIADA",
            enviada_at=datetime.utcnow()
        )
        mock_log = LogAuditoria(
            id=1,
            usuario_id_ref="agresor-uuid",
            tipo_evento="DETECCION_GROOMING_NIVEL_2",
            descripcion="Detección de Grooming",
            hash_integridad="hash"
        )
        mock_db_audit.query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = [
            (mock_alerta, mock_log)
        ]

        dash = parents.get_parent_dashboard(child_user=self.mock_user, db_audit=mock_db_audit)
        self.assertEqual(dash.child_nickname, "ExploradorLunar")
        self.assertEqual(len(dash.alerts), 1)
        self.assertEqual(dash.alerts[0].id, "10")
        self.assertIn("Grooming", dash.alerts[0].title)

    def test_incident_detail_decryption_and_attribution(self):
        raw_evidence = "ExploradorLunar: Hola | Sospechoso: Pásame tu número"
        enc_ev = self.aes.encrypt(raw_evidence)

        mock_log = LogAuditoria(
            id=1,
            usuario_id_ref="agresor-uuid",
            bloque_id_ref=None,
            tipo_evento="DETECCION_GROOMING_NIVEL_2",
            descripcion="Patrón de grooming detectado",
            evidencia_cifrada=enc_ev["ciphertext_b64"],
            iv_nonce=enc_ev["nonce_b64"],
            tag_autenticacion=enc_ev["tag_b64"],
            hash_integridad="hash",
            timestamp_evento=datetime.utcnow()
        )

        mock_alerta = AlertaUsuario(
            id=10,
            usuario_receptor_id_ref=self.mock_user.id,
            usuario_victima_id_ref=self.mock_user.id,
            log_id_ref=1,
            estado="ENVIADA",
            enviada_at=datetime.utcnow()
        )

        mock_db_audit = MagicMock()
        mock_db_audit.query.return_value.filter.return_value.first.side_effect = [mock_alerta, mock_log]
        mock_db = MagicMock()

        detail = parents.get_parent_incident_detail(
            alert_id=10,
            child_user=self.mock_user,
            db=mock_db,
            db_audit=mock_db_audit
        )

        self.assertEqual(detail.id, "10")
        self.assertEqual(len(detail.messages), 2)
        # Mensaje 1 del menor
        self.assertEqual(detail.messages[0].author, "ExploradorLunar")
        self.assertTrue(detail.messages[0].fromChild)
        # Mensaje 2 del atacante
        self.assertEqual(detail.messages[1].author, "Otro jugador")
        self.assertFalse(detail.messages[1].fromChild)
        self.assertIn("Pásame tu número", detail.messages[1].text)
        self.assertIn("Escucha con calma", detail.guidance)


if __name__ == "__main__":
    unittest.main()
