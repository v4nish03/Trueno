# services/backup_service.py
import os
import sqlite3
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from services.telegram_service import enviar_backup_sync


class BackupService:
    """Servicio para manejo de backups con notificación por Telegram"""
    
    def __init__(self):
        self.backup_dir = os.path.join(os.path.dirname(__file__), "..", "backups")
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def crear_backup_sqlite(self, db: Session) -> dict:
        """
        Crea un backup de la base de datos SQLite y lo envía por Telegram
        Retorna: {"exito": bool, "mensaje": str, "archivo": str}
        """
        try:
            # Obtener ruta de la base de datos
            database_url = os.getenv("DATABASE_URL", "sqlite:///./trueno.db")
            if database_url.startswith("sqlite:///"):
                db_path = database_url.replace("sqlite:///", "")
            else:
                return {"exito": False, "mensaje": "Solo se soporta SQLite para backups automáticos"}
            
            # Generar nombre de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"trueno_backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Crear backup
            conn = sqlite3.connect(db_path)
            backup_conn = sqlite3.connect(backup_path)
            conn.backup(backup_conn)
            conn.close()
            backup_conn.close()
            
            # Generar mensaje de resumen
            stats = self._obtener_estadisticas_db(db)
            mensaje = self._formatear_mensaje_backup(backup_filename, stats)
            
            # Enviar notificación por Telegram
            telegram_enviado = enviar_backup_sync(db, mensaje)
            
            # Limpiar backups antiguos (mantener últimos 5)
            self._limpiar_backups_antiguos()
            
            return {
                "exito": True,
                "mensaje": "Backup creado exitosamente",
                "archivo": backup_filename,
                "telegram_enviado": telegram_enviado,
                "estadisticas": stats
            }
            
        except Exception as e:
            error_msg = f"Error creando backup: {str(e)}"
            # Enviar error por Telegram
            try:
                enviar_backup_sync(db, f"❌ {error_msg}")
            except Exception:
                pass
            return {"exito": False, "mensaje": error_msg}
    
    def _obtener_estadisticas_db(self, db: Session) -> dict:
        """Obtener estadísticas básicas de la base de datos"""
        try:
            stats = {}
            
            # Contar productos
            stats["productos"] = db.execute(text("SELECT COUNT(*) FROM productos")).scalar()
            stats["productos_activos"] = db.execute(text("SELECT COUNT(*) FROM productos WHERE activo = 1")).scalar()
            
            # Contar ventas
            stats["ventas_totales"] = db.execute(text("SELECT COUNT(*) FROM ventas")).scalar()
            stats["ventas_hoy"] = db.execute(text("""
                SELECT COUNT(*) FROM ventas 
                WHERE DATE(fecha) = DATE('now')
            """)).scalar()
            
            # Stock bajo
            stats["stock_bajo"] = db.execute(text("""
                SELECT COUNT(*) FROM productos 
                WHERE stock <= stock_minimo
            """)).scalar()
            
            # Ventas sin stock pendientes
            stats["ventas_sin_stock"] = db.execute(text("""
                SELECT SUM(ventas_sin_stock) FROM productos 
                WHERE ventas_sin_stock > 0
            """)).scalar() or 0
            
            return stats
            
        except Exception as e:
            return {"error": str(e)}
    
    def _formatear_mensaje_backup(self, filename: str, stats: dict) -> str:
        """Formatea el mensaje de backup para Telegram"""
        mensaje = [
            f"📦 <b>Backup Automático Trueno Motors</b>",
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "📁 Archivo: " + filename,
            "",
            "<b>📊 Estadísticas del Sistema:</b>"
        ]
        
        if "error" in stats:
            mensaje.append(f"❌ Error obteniendo estadísticas: {stats['error']}")
        else:
            mensaje.append(f"• Productos totales: {stats.get('productos', 0)}")
            mensaje.append(f"• Productos activos: {stats.get('productos_activos', 0)}")
            mensaje.append(f"• Ventas totales: {stats.get('ventas_totales', 0)}")
            mensaje.append(f"• Ventas hoy: {stats.get('ventas_hoy', 0)}")
            mensaje.append(f"• ⚠️ Stock bajo: {stats.get('stock_bajo', 0)}")
            mensaje.append(f"• 🚨 Ventas sin stock: {stats.get('ventas_sin_stock', 0)}")
        
        mensaje.append("\n✅ Backup completado exitosamente")
        
        return "\n".join(mensaje)
    
    def _limpiar_backups_antiguos(self):
        """Elimina backups antiguos, manteniendo solo los 5 más recientes"""
        try:
            files = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith("trueno_backup_") and filename.endswith(".db"):
                    filepath = os.path.join(self.backup_dir, filename)
                    files.append((filepath, os.path.getmtime(filepath)))
            
            # Ordenar por fecha (más antiguo primero)
            files.sort(key=lambda x: x[1])
            
            # Eliminar los más antiguos, manteniendo 5
            for filepath, _ in files[:-5]:
                os.remove(filepath)
                print(f"🗑️ Backup antiguo eliminado: {os.path.basename(filepath)}")
                
        except Exception as e:
            print(f"Error limpiando backups antiguos: {e}")
    
    def programar_backup_diario(self, db: Session):
        """
        Programa un backup diario (debe ser llamado por un scheduler externo)
        """
        resultado = self.crear_backup_sqlite(db)
        
        if resultado["exito"]:
            print(f"✅ Backup diario completado: {resultado['archivo']}")
        else:
            print(f"❌ Error en backup diario: {resultado['mensaje']}")
        
        return resultado


# Instancia global
backup_service = BackupService()


def crear_backup_sync(db: Session) -> dict:
    """Versión síncrona para crear backup"""
    return backup_service.crear_backup_sqlite(db)
