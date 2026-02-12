"""
AegisShare — Database Seed Script

Creates an admin user, an analyst user, and default DLP policies
so the application is ready to use immediately.

Usage:
    python seed.py
"""

import sys
import os

# Ensure the project root is in the Python path.
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine
from app import models
from app.security import get_password_hash


def seed():
    """Populate the database with initial data."""
    # Create all tables (safe to call multiple times).
    models.Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # ---------------------------------------------------------------
        # Users
        # ---------------------------------------------------------------
        users_data = [
            {
                "email": "admin@aegisshare.com",
                "full_name": "Administrador",
                "password": "admin123",
                "role": "admin",
            },
            {
                "email": "analyst@aegisshare.com",
                "full_name": "Analista DLP",
                "password": "analyst123",
                "role": "analyst",
            },
        ]

        for u in users_data:
            exists = db.query(models.User).filter(models.User.email == u["email"]).first()
            if exists:
                print(f"  ⏭️  Usuario ya existe: {u['email']}")
                continue

            user = models.User(
                email=u["email"],
                full_name=u["full_name"],
                hashed_password=get_password_hash(u["password"]),
                role=u["role"],
            )
            db.add(user)
            print(f"  ✅ Usuario creado: {u['email']} (rol: {u['role']}, password: {u['password']})")

        db.commit()

        # ---------------------------------------------------------------
        # Default DLP Policies
        # ---------------------------------------------------------------
        policies_data = [
            {"entity_type": "PERSON", "display_name": "Nombre de Persona", "action": "warn", "min_confidence": 0.6},
            {"entity_type": "EMAIL_ADDRESS", "display_name": "Correo Electrónico", "action": "block", "min_confidence": 0.5},
            {"entity_type": "PHONE_NUMBER", "display_name": "Número Telefónico", "action": "block", "min_confidence": 0.4},
            {"entity_type": "CREDIT_CARD", "display_name": "Tarjeta de Crédito", "action": "block", "min_confidence": 0.3},
            {"entity_type": "US_SSN", "display_name": "Número de Seguro Social (US)", "action": "block", "min_confidence": 0.3},
            {"entity_type": "IP_ADDRESS", "display_name": "Dirección IP", "action": "warn", "min_confidence": 0.6},
            {"entity_type": "IBAN_CODE", "display_name": "Código IBAN", "action": "block", "min_confidence": 0.4},
            {"entity_type": "US_DRIVER_LICENSE", "display_name": "Licencia de Conducir (US)", "action": "block", "min_confidence": 0.4},
            {"entity_type": "LOCATION", "display_name": "Ubicación", "action": "ignore", "min_confidence": 0.7},
            {"entity_type": "DATE_TIME", "display_name": "Fecha / Hora", "action": "ignore", "min_confidence": 0.8},
        ]

        for p in policies_data:
            exists = (
                db.query(models.DlpPolicy)
                .filter(models.DlpPolicy.entity_type == p["entity_type"])
                .first()
            )
            if exists:
                print(f"  ⏭️  Política ya existe: {p['entity_type']}")
                continue

            policy = models.DlpPolicy(**p)
            db.add(policy)
            print(f"  ✅ Política creada: {p['display_name']} ({p['action']})")

        db.commit()

        print("\n🎉 Seed completado exitosamente!")
        print("\n📋 Credenciales de acceso:")
        print("   Admin   → admin@aegisshare.com   / admin123")
        print("   Analyst → analyst@aegisshare.com  / analyst123")

    finally:
        db.close()


if __name__ == "__main__":
    print("\n🌱 AegisShare — Seeding database...\n")
    seed()
