# services/impresora_service.py
import os
import subprocess
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from models.configuracion import Configuracion


class ImpresoraService:
    """Servicio para impresión de recibos en impresora térmica"""
    
    def __init__(self):
        self.impresora_por_defecto = "TM-T20II"  # Modelo común de Epson
    
    def obtener_impresora_configurada(self, db: Session) -> str:
        """Obtener el nombre de la impresora configurada"""
        config = db.query(Configuracion).filter(
            Configuracion.clave == "impresora_termino",
            Configuracion.activo.is_(True)
        ).first()
        
        return config.valor if config else self.impresora_por_defecto
    
    def generar_texto_recibo(self, datos_recibo: Dict[str, Any]) -> str:
        """
        Generar el texto formateado para impresora térmica
        Formato ESC/POS para impresoras térmicas
        """
        lineas = []
        
        # Encabezado - centrado y en negrita
        lineas.append(chr(27) + chr(33) + chr(8))  # Doble altura
        lineas.append(chr(27) + chr(97) + chr(1))   # Centrado
        lineas.append("TRUENO MOTORS")
        lineas.append("UYUNI")
        lineas.append(chr(27) + chr(33) + chr(0))  # Normal
        lineas.append("================================")
        lineas.append(chr(27) + chr(97) + chr(0))   # Izquierda
        
        # Información de la venta
        lineas.append(f"RECIBO N°: {datos_recibo.get('venta_id', 'N/A')}")
        lineas.append(f"FECHA: {datos_recibo.get('fecha', datetime.now()).strftime('%d/%m/%Y %H:%M')}")
        lineas.append("")
        
        # Productos
        lineas.append("PRODUCTOS:")
        lineas.append("--------------------------------")
        
        items = datos_recibo.get('items', [])
        for item in items:
            nombre = item['nombre'][:20]  # Limitar a 20 caracteres
            cantidad = item['cantidad']
            precio = item['precio_unitario']
            subtotal = item['subtotal']
            
            lineas.append(f"{cantidad}x {nombre}")
            lineas.append(f"  ${precio:.2f} c/u = ${subtotal:.2f}")
        
        lineas.append("--------------------------------")
        
        # Total
        lineas.append(chr(27) + chr(33) + chr(8))  # Doble altura
        lineas.append(f"TOTAL: ${datos_recibo.get('total', 0):.2f}")
        lineas.append(chr(27) + chr(33) + chr(0))  # Normal
        
        # Método de pago
        metodo = datos_recibo.get('metodo_pago', 'efectivo')
        metodo_str = "EFECTIVO" if metodo == "efectivo" else "QR"
        lineas.append(f"PAGO: {metodo_str}")
        
        # Pie de página
        lineas.append("")
        lineas.append(chr(27) + chr(97) + chr(1))   # Centrado
        lineas.append("¡Gracias por su compra!")
        lineas.append("")
        
        # Código QR (si está disponible)
        qr_codigo = datos_recibo.get('qr_codigo')
        if qr_codigo:
            lineas.append("CÓDIGO QR:")
            lineas.append(qr_codigo)
        
        lineas.append("")
        lineas.append(chr(27) + chr(97) + chr(0))   # Izquierda
        
        # Cortar papel
        lineas.append(chr(29) + chr(86) + chr(66))  # Corte parcial
        lineas.append(chr(29) + chr(86) + chr(0))   # Corte completo
        
        return "\n".join(lineas)
    
    def imprimir_recibo_escpos(self, db: Session, datos_recibo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Imprimir recibo usando comandos ESC/POS
        Retorna: {"exito": bool, "mensaje": str}
        """
        try:
            # Obtener impresora configurada
            nombre_impresora = self.obtener_impresora_configurada(db)
            
            # Generar texto del recibo
            texto_recibo = self.generar_texto_recibo(datos_recibo)
            
            # Intentar imprimir usando lp (sistema Linux)
            resultado = self._imprimir_con_lp(texto_recibo, nombre_impresora)
            
            if resultado["exito"]:
                return {
                    "exito": True,
                    "mensaje": f"Recibo impreso en {nombre_impresora}",
                    "impresora": nombre_impresora
                }
            else:
                # Si lp falla, intentar con método alternativo
                return self._imprimir_alternativa(texto_recibo, nombre_impresora)
                
        except Exception as e:
            return {
                "exito": False,
                "mensaje": f"Error imprimiendo recibo: {str(e)}"
            }
    
    def _imprimir_con_lp(self, texto: str, impresora: str) -> Dict[str, Any]:
        """Imprimir usando comando lp de Linux"""
        try:
            # Crear archivo temporal
            temp_file = "/tmp/recibo_temp.txt"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(texto)
            
            # Imprimir usando lp
            comando = f"lp -d '{impresora}' -o raw '{temp_file}'"
            resultado = subprocess.run(
                comando, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            # Limpiar archivo temporal
            try:
                os.remove(temp_file)
            except Exception:
                pass
            
            if resultado.returncode == 0:
                return {"exito": True, "mensaje": "Impresión exitosa"}
            else:
                return {
                    "exito": False, 
                    "mensaje": f"Error lp: {resultado.stderr}"
                }
                
        except subprocess.TimeoutExpired:
            return {"exito": False, "mensaje": "Timeout en impresión"}
        except Exception as e:
            return {"exito": False, "mensaje": f"Error: {str(e)}"}
    
    def _imprimir_alternativa(self, texto: str, impresora: str) -> Dict[str, Any]:
        """Método alternativo de impresión"""
        try:
            # Intentar con lpr
            temp_file = "/tmp/recibo_temp.txt"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(texto)
            
            comando = f"lpr -P '{impresora}' '{temp_file}'"
            resultado = subprocess.run(
                comando, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            try:
                os.remove(temp_file)
            except Exception:
                pass
            
            if resultado.returncode == 0:
                return {
                    "exito": True, 
                    "mensaje": f"Recibo impreso con lpr en {impresora}"
                }
            else:
                return {
                    "exito": False, 
                    "mensaje": f"Error lpr: {resultado.stderr}"
                }
                
        except Exception as e:
            return {
                "exito": False, 
                "mensaje": f"Error método alternativo: {str(e)}"
            }
    
    def verificar_impresora(self, db: Session) -> Dict[str, Any]:
        """
        Verificar si la impresora está disponible
        Retorna: {"disponible": bool, "mensaje": str, "impresora": str}
        """
        try:
            nombre_impresora = self.obtener_impresora_configurada(db)
            
            # Verificar si la impresora existe en el sistema
            comando = f"lpstat -p '{nombre_impresora}'"
            resultado = subprocess.run(
                comando, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=5
            )
            
            if resultado.returncode == 0:
                return {
                    "disponible": True,
                    "mensaje": f"Impresora {nombre_impresora} disponible",
                    "impresora": nombre_impresora,
                    "estado": resultado.stdout
                }
            else:
                return {
                    "disponible": False,
                    "mensaje": f"Impresora {nombre_impresora} no encontrada",
                    "impresora": nombre_impresora,
                    "error": resultado.stderr
                }
                
        except Exception as e:
            return {
                "disponible": False,
                "mensaje": f"Error verificando impresora: {str(e)}",
                "impresora": nombre_impresora
            }
    
    def listar_impresoras_disponibles(self) -> Dict[str, Any]:
        """
        Listar todas las impresoras disponibles en el sistema
        """
        try:
            comando = "lpstat -p"
            resultado = subprocess.run(
                comando, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=5
            )
            
            if resultado.returncode == 0:
                # Parsear salida para extraer nombres de impresoras
                lineas = resultado.stdout.split('\n')
                impresoras = []
                
                for linea in lineas:
                    if 'printer' in linea and 'is idle' in linea:
                        # Extraer nombre de impresora
                        partes = linea.split(' ')
                        for i, parte in enumerate(partes):
                            if parte == 'printer':
                                if i + 1 < len(partes):
                                    nombre = partes[i + 1].strip()
                                    impresoras.append(nombre)
                                break
                
                return {
                    "exito": True,
                    "impresoras": impresoras,
                    "total": len(impresoras)
                }
            else:
                return {
                    "exito": False,
                    "mensaje": "Error listando impresoras",
                    "error": resultado.stderr
                }
                
        except Exception as e:
            return {
                "exito": False,
                "mensaje": f"Error: {str(e)}"
            }


# Instancia global
impresora_service = ImpresoraService()


def imprimir_recibo_sync(db: Session, datos_recibo: Dict[str, Any]) -> Dict[str, Any]:
    """Versión síncrona para imprimir recibo"""
    return impresora_service.imprimir_recibo_escpos(db, datos_recibo)
