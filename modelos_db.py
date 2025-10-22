"""
Modelos de base de datos con SQLAlchemy.
Mapea las clases Python a tablas PostgreSQL.
"""

from sqlalchemy import create_engine, Column, Integer, String, Date, Time, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear base
Base = declarative_base()

# Configurar conexión a PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL')

# Render usa "postgres://" pero SQLAlchemy necesita "postgresql://"
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

# Modelos de tablas

class PacienteDB(Base):
    """Tabla de pacientes"""
    __tablename__ = 'pacientes'
    
    cedula = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    
    # Relación con evoluciones (un paciente tiene muchas evoluciones)
    evoluciones = relationship("EvolucionDB", back_populates="paciente", cascade="all, delete-orphan")

class EvolucionDB(Base):
    """Tabla de evoluciones"""
    __tablename__ = 'evoluciones'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cedula_paciente = Column(Integer, ForeignKey('pacientes.cedula'), nullable=False)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    contenido = Column(Text, nullable=False)
    retraso = Column(JSON)  # Guardamos el dict de retraso como JSON
    
    # Relación con paciente
    paciente = relationship("PacienteDB", back_populates="evoluciones")

class StrikeDB(Base):
    """Tabla de strikes"""
    __tablename__ = 'strikes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    razon = Column(String(255), nullable=False)
    fecha = Column(String(50), nullable=False)

# Función para crear todas las tablas
def crear_tablas():
    """Crea todas las tablas en la base de datos"""
    Base.metadata.create_all(engine)
    print("✅ Tablas creadas exitosamente")

# Función para obtener sesión
def obtener_sesion():
    """Retorna una nueva sesión de base de datos"""
    return Session()