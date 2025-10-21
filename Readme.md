# Sistema de Registro de Evoluciones Médicas

## Descripción
Sistema de gestión de evoluciones médicas. 
Permite registrar pacientes, subir evoluciones de terapia, controlar retrasos 
y generar reportes.

## Características
- ✅ CRUD completo de pacientes y evoluciones
- ✅ Control automático de retrasos (más de 24 horas)
- ✅ Sistema de strikes para incumplimientos
- ✅ Logging de todas las acciones
- ✅ Persistencia en JSON
- ✅ Validaciones robustas

## Instalación
```bash
pip install -r requirements.txt
```

## Uso
```bash
python main.py
```

## Estructura del Proyecto
```
proyecto_medico/
├── modelos.py           # Clases principales
├── persistencia.py      # Guardado/carga de datos
├── utils.py             # Funciones auxiliares
├── menu.py              # Interfaz de usuario
├── logger.py            # Sistema de logging
├── main.py              # Punto de entrada
├── tests/               # Tests unitarios
└── logs/                # Archivos de log
```

## Requisitos
- Python 3.8+
- pytest (para tests)

## Próximas Fases
- [ ] Análisis con Pandas
- [ ] Detección de similitudes con Difflib
- [ ] Interfaz web con Flask