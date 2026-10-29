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

from backend.api import appeals
from backend.database.models import Usuario, Apelacion, BloqueAnalisis
from backend.database.models_auditoria import LogAuditoria
from backend.database.schemas import AdminLoginRequest, AdminAppealResolveRequest, UserAppealSubmitRequest
from backend.api.jwt_manager import verify_access_token


class TestAppealsAPIUnit(unittest.TestCase):

    def setUp(self):
        self.mock_admin_user = "admin.animoon"
        self.banned_user = Usuario(
            id="banned-uuid-999",
            nickname="CometaAzul",
            telefono_cifrado="cifrado",
            telefono_iv_nonce="iv",
            telefono_tag="tag",
            argon2id_hash="hash",
            salt="salt",
            is_verified=True,
            is_active=False,
            is_banned=True
        )

    def test_admin_login_success(self):
        req = AdminLoginRequest(username="admin.animoon", password="AdminDemo#2026")
        res = appeals.admin_login(req)
        self.assertEqual(res.status, "success")
        self.assertIsNotNone(res.admin_token)

        payload = verify_access_token(res.admin_token)
        self.assertEqual(payload["role"], "admin")
        self.assertEqual(payload["sub"], "admin.animoon")

    def test_admin_login_wrong_credentials(self):
        from fastapi import HTTPException
        req = AdminLoginRequest(username="admin.animoon", password="WrongPassword")
        with self.assertRaises(HTTPException) as cm:
            appeals.admin_login(req)
        self.assertEqual(cm.exception.status_code, 401)

    def test_list_appeals(self):
        mock_db = MagicMock()
        mock_db_audit = MagicMock()

        # Simulamos que hay una apelación en BD
        ap = Apelacion(
            id="AP-TEST-001",
            usuario_id=self.banned_user.id,
            bloque_id="bloque-123",
            justificacion="Fue una confusión en el juego",
            estado="PENDIENTE",
            created_at=datetime.utcnow()
        )
        mock_db.query.return_value.order_by.return_value.all.return_value = [ap]
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            self.banned_user,  # usuario
            BloqueAnalisis(id="bloque-123", chat_id="sala-1", numero_bloque=1, fase_detectada="NIVEL_2_GROOMING", modelo_version="BETO") # bloque
        ]
        mock_db_audit.query.return_value.filter.return_value.first.return_value = None

        res = appeals.list_appeals(
            admin_user="admin.animoon",
            db=mock_db,
            db_audit=mock_db_audit
        )
        self.assertGreaterEqual(len(res), 1)
        self.assertEqual(res[0].id, "AP-TEST-001")
        self.assertEqual(res[0].nickname, "CometaAzul")
        self.assertEqual(res[0].status, "PENDING")

    def test_mark_appeal_in_review(self):
        mock_db = MagicMock()
        ap = Apelacion(
            id="AP-TEST-001",
            usuario_id=self.banned_user.id,
            bloque_id="bloque-123",
            justificacion="Justificación",
            estado="PENDIENTE"
        )
        mock_db.query.return_value.filter.return_value.first.return_value = ap

        res = appeals.mark_appeal_in_review(
            appeal_id="AP-TEST-001",
            admin_user="admin.animoon",
            db=mock_db
        )
        self.assertEqual(res.status, "success")
        self.assertEqual(ap.estado, "EN_REVISION")
        mock_db.commit.assert_called_once()

    def test_resolve_appeal_approve_unbans_user(self):
        mock_db = MagicMock()
        mock_db_audit = MagicMock()

        ap = Apelacion(
            id="AP-TEST-001",
            usuario_id=self.banned_user.id,
            bloque_id="bloque-123",
            justificacion="Pido disculpas",
            estado="EN_REVISION",
            created_at=datetime.utcnow()
        )
        # first call -> apelacion, second call -> usuario
        mock_db.query.return_value.filter.return_value.first.side_effect = [ap, self.banned_user, self.banned_user]

        req = AdminAppealResolveRequest(approved=True, reason="Explicación aceptada tras revisión.")

        with patch("backend.api.appeals.reactivar_usuario_en_redis") as mock_redis:
            res = appeals.resolve_appeal(
                appeal_id="AP-TEST-001",
                req=req,
                admin_user="admin.animoon",
                db=mock_db,
                db_audit=mock_db_audit
            )

            self.assertEqual(res.status, "APPROVED")
            self.assertEqual(res.resolution, "Explicación aceptada tras revisión.")
            self.assertEqual(ap.estado, "APROBADA")
            # El usuario debe quedar desbaneado y activo
            self.assertFalse(self.banned_user.is_banned)
            self.assertTrue(self.banned_user.is_active)
            mock_redis.assert_called_once_with(self.banned_user.id)
            mock_db.commit.assert_called()

    def test_submit_appeal_success(self):
        mock_db = MagicMock()
        self.banned_user.is_banned = True
        mock_db.query.return_value.filter.return_value.first.return_value = self.banned_user
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

        req = UserAppealSubmitRequest(
            nickname="CometaAzul",
            justificacion="Quiero explicar que fue un malentendido en el chat de minijuego."
        )

        res = appeals.submit_appeal(req=req, db=mock_db)
        self.assertEqual(res.status, "success")
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
