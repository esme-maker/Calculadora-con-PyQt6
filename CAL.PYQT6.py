import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QKeyEvent
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollBar,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class Calculadora(QMainWindow):
    BLANCO = "#FFFFFF"
    ROSA_FONDO = "#FDEFF4"
    ROSA_PASTEL = "#FBD5E3"
    ROSA = "#F6B9D0"
    ROSA_TEXTO = "#C98BA6"
    TINTA = "#8A4B66"

    LIMITE_HISTORIAL = 50

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora")
        self.setFixedSize(460, 700)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.ROSA_FONDO};
            }}
            QPushButton {{
                border: none;
                font-family: "Segoe UI";
            }}
            QPushButton:hover {{
                border: none;
            }}
            QPushButton:focus {{
                outline: none;
            }}
        """)

        self.numero = "0"
        self.texto_izquierda = ""
        self.pendiente_operador = ""
        self.acumulado = None
        self.esperando_numero = True
        self.resultado_mostrado = False
        self.historial = []
        self.ventana_historial = None

        self.crear_interfaz()

    # ------------------------------------------------------------------ UI
    def crear_interfaz(self):
        central = QWidget()
        self.setCentralWidget(central)

        raiz = QVBoxLayout(central)
        raiz.setContentsMargins(20, 0, 20, 20)
        raiz.setSpacing(0)

        titulo = QLabel("Calculadora")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setFont(QFont("Segoe UI", 19, QFont.Weight.Bold))
        titulo.setStyleSheet(f"color: {self.ROSA_TEXTO};")
        titulo.setContentsMargins(0, 16, 0, 16)
        raiz.addWidget(titulo)

        marco_pantalla = QFrame()
        marco_pantalla.setStyleSheet(
            f"background-color: {self.ROSA_PASTEL}; border-radius: 10px;"
        )
        layout_marco = QVBoxLayout(marco_pantalla)
        layout_marco.setContentsMargins(4, 4, 4, 4)

        self.etiqueta_pantalla = QLabel("0")
        self.etiqueta_pantalla.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.etiqueta_pantalla.setFont(QFont("Consolas", 28, QFont.Weight.Bold))
        self.etiqueta_pantalla.setStyleSheet(
            f"""
            background-color: {self.BLANCO};
            color: {self.TINTA};
            border-radius: 8px;
            padding: 12px 16px;
        """
        )
        self.etiqueta_pantalla.setMinimumHeight(64)
        self.etiqueta_pantalla.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout_marco.addWidget(self.etiqueta_pantalla)
        raiz.addWidget(marco_pantalla)
        raiz.addSpacing(10)

        self.boton_historial = self.crear_boton(
            "Historial", self.abrir_historial, "claro"
        )
        raiz.addWidget(self.boton_historial)
        raiz.addSpacing(14)

        panel_botones = QWidget()
        raiz.addWidget(panel_botones, stretch=1)
        layout_botones = QVBoxLayout(panel_botones)
        layout_botones.setContentsMargins(0, 0, 0, 0)
        layout_botones.setSpacing(10)

        botones = [
            [
                ("C", self.limpiar, "claro"),
                ("⌫", self.borrar, "claro"),
                ("%", self.porcentaje, "claro"),
                ("÷", lambda: self.operar("/"), "operador"),
            ],
            [
                ("7", lambda: self.introducir("7"), "numero"),
                ("8", lambda: self.introducir("8"), "numero"),
                ("9", lambda: self.introducir("9"), "numero"),
                ("×", lambda: self.operar("*"), "operador"),
            ],
            [
                ("4", lambda: self.introducir("4"), "numero"),
                ("5", lambda: self.introducir("5"), "numero"),
                ("6", lambda: self.introducir("6"), "numero"),
                ("−", lambda: self.operar("-"), "operador"),
            ],
            [
                ("1", lambda: self.introducir("1"), "numero"),
                ("2", lambda: self.introducir("2"), "numero"),
                ("3", lambda: self.introducir("3"), "numero"),
                ("+", lambda: self.operar("+"), "operador"),
            ],
            [
                ("±", self.cambiar_signo, "claro"),
                ("0", lambda: self.introducir("0"), "numero"),
                (".", lambda: self.introducir("."), "numero"),
                ("=", self.igual, "igual"),
            ],
        ]

        for fila, botones_fila in enumerate(botones):
            layout_fila = QHBoxLayout()
            layout_fila.setContentsMargins(0, 0, 0, 0)
            layout_fila.setSpacing(10)
            for texto, comando, tipo in botones_fila:
                boton = self.crear_boton(texto, comando, tipo)
                layout_fila.addWidget(boton, stretch=1)
            layout_botones.addLayout(layout_fila, stretch=1)

    def crear_boton(self, texto, comando, tipo):
        tamano_fuente = 13 if texto == "Historial" else 17
        boton = QPushButton(texto)
        boton.setFont(QFont("Segoe UI", tamano_fuente, QFont.Weight.Bold))
        boton.setCursor(Qt.CursorShape.PointingHandCursor)
        boton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        boton.setMinimumHeight(38 if texto == "Historial" else 44)
        boton.setAutoFillBackground(False)
        boton.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self.color_botones(tipo)};
                color: {self.color_texto(tipo)};
                border: none;
                border-radius: 8px;
                padding: 6px 10px;
            }}
            QPushButton:hover {{
                background-color: {self.color_activo(tipo)};
                color: {self.color_texto_activo(tipo)};
            }}
            QPushButton:pressed {{
                background-color: {self.color_activo(tipo)};
                color: {self.color_texto_activo(tipo)};
            }}
            """
        )
        boton.clicked.connect(lambda _checked=False, accion=comando: accion())
        return boton

    def color_botones(self, tipo):
        if tipo == "igual":
            return self.ROSA_TEXTO
        if tipo == "operador":
            return self.ROSA
        if tipo == "claro":
            return self.ROSA_PASTEL
        return self.BLANCO

    def color_texto(self, tipo):
        return self.BLANCO if tipo == "igual" else self.TINTA

    def color_activo(self, tipo):
        if tipo == "igual":
            return self.TINTA
        if tipo == "numero":
            return self.ROSA_FONDO
        return self.ROSA

    def color_texto_activo(self, tipo):
        return self.BLANCO if tipo == "igual" else self.TINTA

    # ------------------------------------------------------------- teclado
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if not event.modifiers() & ~Qt.KeyboardModifier.KeypadModifier:
            tecla = event.key()
            mapa_texto = {
                Qt.Key.Key_Return: self.igual,
                Qt.Key.Key_Enter: self.igual,
                Qt.Key.Key_Escape: self.limpiar,
                Qt.Key.Key_Backspace: self.borrar,
                Qt.Key.Key_Percent: self.porcentaje,
                Qt.Key.Key_Plus: lambda: self.operar("+"),
                Qt.Key.Key_Minus: lambda: self.operar("-"),
                Qt.Key.Key_Asterisk: lambda: self.operar("*"),
                Qt.Key.Key_Slash: lambda: self.operar("/"),
                Qt.Key.Key_H: self.abrir_historial,
            }
            if tecla in mapa_texto:
                mapa_texto[tecla]()
                return
            if Qt.Key.Key_0 <= tecla <= Qt.Key.Key_9:
                self.introducir(chr(tecla))
                return
        super().keyPressEvent(event)

    # ------------------------------------------------------------- calculo
    def refrescar_pantalla(self):
        self.etiqueta_pantalla.setText(
            self.texto_izquierda + self.pendiente_operador + self.numero
        )

    def introducir(self, valor):
        if self.resultado_mostrado:
            self.reiniciar_operacion()
            self.numero = ""

        texto = self.numero
        if valor == ".":
            if "." not in texto:
                self.numero = (texto if texto else "0") + "."
        elif texto in ("", "0"):
            self.numero = valor
        elif texto in ("-", "-0"):
            self.numero = "-" + valor
        else:
            self.numero = texto + valor

        self.esperando_numero = False
        self.refrescar_pantalla()

    def valor_actual(self):
        try:
            return float(self.numero)
        except ValueError:
            return 0.0

    def formatear(self, numero):
        if abs(numero) < 1e-12:
            return "0"
        if numero.is_integer() and abs(numero) < 1e15:
            return str(int(numero))
        return f"{numero:.12g}"

    def calcular(self, izquierda, derecha, operador):
        if operador == "+":
            return izquierda + derecha
        if operador == "-":
            return izquierda - derecha
        if operador == "*":
            return izquierda * derecha
        if operador == "/":
            if derecha == 0:
                raise ZeroDivisionError
            return izquierda / derecha
        raise ValueError

    def operar(self, operador):
        if self.pendiente_operador and not self.esperando_numero:
            derecha = self.valor_actual()
            try:
                resultado = self.calcular(
                    self.acumulado, derecha, self.pendiente_operador
                )
            except ZeroDivisionError:
                self.mostrar_error(
                    self.acumulado, derecha, self.pendiente_operador
                )
                return
            self.acumulado = resultado
            self.texto_izquierda = self.formatear(resultado)
        else:
            self.acumulado = self.valor_actual()
            self.texto_izquierda = self.formatear(self.acumulado)

        self.pendiente_operador = operador
        self.esperando_numero = True
        self.resultado_mostrado = False
        self.numero = ""
        self.refrescar_pantalla()

    def igual(self):
        if not self.pendiente_operador or self.acumulado is None:
            return
        if self.esperando_numero and self.numero == "":
            return

        izquierda = self.formatear(self.acumulado)
        derecha = self.valor_actual()
        operador = self.pendiente_operador

        try:
            resultado = self.calcular(self.acumulado, derecha, operador)
        except ZeroDivisionError:
            self.mostrar_error(self.acumulado, derecha, operador)
            return

        self.registrar(
            f"{izquierda} {operador} {self.formatear(derecha)} = "
            f"{self.formatear(resultado)}"
        )

        self.numero = self.formatear(resultado)
        self.texto_izquierda = ""
        self.pendiente_operador = ""
        self.acumulado = None
        self.esperando_numero = True
        self.resultado_mostrado = True
        self.refrescar_pantalla()

    def porcentaje(self):
        self.numero = self.formatear(self.valor_actual() / 100)
        self.esperando_numero = False
        self.resultado_mostrado = False
        self.refrescar_pantalla()

    def cambiar_signo(self):
        texto = self.numero
        if texto == "":
            return
        if texto.startswith("-"):
            self.numero = texto[1:]
        elif texto != "0":
            self.numero = "-" + texto
        self.refrescar_pantalla()

    def registrar(self, texto):
        self.historial.append(texto)
        if len(self.historial) > self.LIMITE_HISTORIAL:
            del self.historial[0]
        self.actualizar_historial()

    def mostrar_error(self, izquierda, derecha, operador):
        self.registrar(
            f"{self.formatear(izquierda)} {operador} {self.formatear(derecha)}"
            " = Error (división entre cero)"
        )
        self.reiniciar_operacion()
        self.numero = "Error"
        self.esperando_numero = True
        self.resultado_mostrado = True
        self.refrescar_pantalla()
        self.mostrar_mensaje_error()

    def mostrar_mensaje_error(self):
        caja = QMessageBox(self)
        caja.setWindowTitle("División entre cero")
        caja.setIcon(QMessageBox.Icon.Critical)
        caja.setText("No se puede dividir entre cero.")
        caja.exec()

    def borrar(self):
        if self.resultado_mostrado:
            self.limpiar()
            return

        texto = self.numero
        if texto:
            self.numero = texto[:-1] if len(texto) > 1 else ""
        elif self.pendiente_operador:
            self.pendiente_operador = ""
            self.texto_izquierda = self.texto_izquierda[:-1]
            self.acumulado = None

        self.refrescar_pantalla()

    def limpiar(self):
        self.reiniciar_operacion()
        self.numero = "0"
        self.refrescar_pantalla()

    def reiniciar_operacion(self):
        self.texto_izquierda = ""
        self.pendiente_operador = ""
        self.acumulado = None
        self.esperando_numero = True
        self.resultado_mostrado = False

    # ------------------------------------------------------------ historial
    def abrir_historial(self):
        if self.ventana_historial is not None and self.ventana_historial.isVisible():
            self.ventana_historial.raise_()
            self.ventana_historial.activateWindow()
            return

        ventana = VentanaHistorial(self)
        ventana.lista_historial.itemDoubleClicked.connect(
            lambda _item: self.reusar()
        )
        ventana.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        ventana.destroyed.connect(self._ventana_historial_destruida)
        self.ventana_historial = ventana
        self.actualizar_historial()
        ventana.show()

    def _ventana_historial_destruida(self, _objeto=None):
        self.ventana_historial = None

    def reusar(self):
        if self.ventana_historial is None:
            return
        fila = self.ventana_historial.lista_historial.currentRow()
        if fila < 0 or fila >= len(self.historial):
            return

        resultado = self.historial[fila].split(" = ")[-1]
        if resultado.startswith("Error"):
            QMessageBox.warning(
                self,
                "Operación no válida",
                "Esa operación dio error, no se puede reutilizar.",
            )
            return

        self.reiniciar_operacion()
        self.numero = resultado
        self.esperando_numero = True
        self.resultado_mostrado = True
        self.refrescar_pantalla()
        self.ventana_historial.close()
        self.ventana_historial = None

    def borrar_historial(self):
        if not self.historial:
            return
        confirmacion = QMessageBox.question(
            self,
            "Borrar historial",
            "¿Seguro que quieres borrar todo el historial?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirmacion == QMessageBox.StandardButton.Yes:
            self.historial.clear()
            self.actualizar_historial()

    def actualizar_historial(self):
        ventana = self.ventana_historial
        if ventana is None:
            return
        lista = ventana.lista_historial
        lista.clear()
        for indice, operacion in enumerate(self.historial, start=1):
            lista.addItem(f"{indice}. {operacion}")
        lista.scrollToBottom()


class VentanaHistorial(QDialog):
    def __init__(self, padre):
        super().__init__(padre)
        self.setWindowTitle("Historial de operaciones")
        self.setFixedSize(380, 330)
        self.setWindowFlag(Qt.WindowType.Window, True)

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(12, 10, 12, 10)
        raiz.setSpacing(10)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {padre.ROSA_PASTEL};
            }}
            QLabel {{
                color: {padre.ROSA_TEXTO};
                font-family: "Segoe UI";
                font-size: 15px;
                font-weight: bold;
                background: transparent;
            }}
            QListWidget {{
                background-color: {padre.BLANCO};
                color: {padre.TINTA};
                border: none;
                font-family: "Consolas";
                font-size: 11px;
            }}
            QListWidget::item:selected {{
                background-color: {padre.ROSA};
                color: {padre.TINTA};
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 10px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {padre.ROSA};
                border-radius: 5px;
                min-height: 24px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QPushButton {{
                border: none;
                border-radius: 6px;
                font-family: "Segoe UI";
                font-size: 12px;
                font-weight: bold;
                padding: 8px 10px;
            }}
        """)

        titulo = QLabel("Historial")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        raiz.addWidget(titulo)

        self.lista_historial = QListWidget()
        self.lista_historial.setSelectionMode(
            QListWidget.SelectionMode.SingleSelection
        )
        self.lista_historial.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        barra = QScrollBar(Qt.Orientation.Vertical)
        barra.valueChanged.connect(self.lista_historial.verticalScrollBar().setValue)
        self.lista_historial.setVerticalScrollBar(barra)
        raiz.addWidget(self.lista_historial, stretch=1)

        botones = QWidget()
        layout_botones = QHBoxLayout(botones)
        layout_botones.setContentsMargins(0, 0, 0, 0)
        layout_botones.setSpacing(10)
        raiz.addWidget(botones)

        self.boton_reusar = QPushButton("Reusar")
        self.boton_reusar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.boton_reusar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.boton_reusar.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {padre.BLANCO};
                color: {padre.TINTA};
            }}
            QPushButton:hover {{
                background-color: {padre.ROSA};
                color: {padre.TINTA};
            }}
            """
        )
        self.boton_reusar.clicked.connect(padre.reusar)
        layout_botones.addWidget(self.boton_reusar, stretch=1)

        self.boton_borrar = QPushButton("Borrar historial")
        self.boton_borrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.boton_borrar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.boton_borrar.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {padre.ROSA_TEXTO};
                color: {padre.BLANCO};
            }}
            QPushButton:hover {{
                background-color: {padre.TINTA};
                color: {padre.BLANCO};
            }}
            """
        )
        self.boton_borrar.clicked.connect(padre.borrar_historial)
        layout_botones.addWidget(self.boton_borrar, stretch=1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Calculadora()
    ventana.show()
    sys.exit(app.exec())