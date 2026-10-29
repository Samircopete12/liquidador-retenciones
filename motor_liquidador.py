#!/usr/bin/env python3
"""Motor del liquidador de retenciones Colombia 2026 — script para uso real.

Este módulo es el mismo motor del notebook ``liquidador.ipynb`` (retefuente,
reteIVA y reteICA por separado, con asientos, certificados, checklist y
auditoría), empaquetado para ejecutarse fuera de Jupyter:

    python motor_liquidador.py plantilla
    python motor_liquidador.py calcular --entrada plantilla_factura.json --usuario "contador@empresa.com"
    python motor_liquidador.py calcular --entrada lote.json --repositorio registradas.json --salida salidas
    python motor_liquidador.py casos

Entrada: un archivo JSON con ``comprador``, ``proveedor`` y ``operaciones``
(ver ``plantilla``). Salida: resumen por consola y, opcionalmente, archivos
JSON (liquidación completa con auditoría) y CSV (asientos y certificados)
en el directorio ``--salida``.

Códigos de salida: 0 = todo liquidado; 1 = error de entrada/archivos;
2 = una o más operaciones fueron bloqueadas por el motor (revisión humana).

Advertencia: proyecto educativo. Verifique la norma, la UVT y las tablas
antes de usarlo en una empresa real.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Any, Sequence




def mostrar(objeto: Any) -> None:
    """Muestra un DataFrame en Jupyter y lo imprime si se ejecuta como script."""
    if pd is not None and isinstance(objeto, pd.DataFrame) and _display is print:
        print(objeto.to_string(index=False))
    else:
        _display(objeto)


def D(valor: Any) -> Decimal:
    """Convierte a Decimal sin pasar por float (evita 0.1 + 0.2)."""
    if isinstance(valor, Decimal):
        return valor
    if isinstance(valor, bool):
        raise TypeError("Un booleano no es un valor monetario.")
    return Decimal(str(valor))


CENTAVO = D("0.01")
CERO = D("0")


def redondear(valor: Any) -> Decimal:
    """Política única de redondeo: dos decimales, half-up."""
    return D(valor).quantize(CENTAVO, rounding=ROUND_HALF_UP)


def dinero(valor: Any) -> Decimal:
    return redondear(valor)


def cop(valor: Any) -> str:
    """Formato de moneda colombiana para leer los resultados."""
    numero = f"{D(valor):,.2f}"
    return "$" + numero.replace(",", "X").replace(".", ",").replace("X", ".")


def porcentaje(valor: Any) -> str:
    numero = f"{D(valor) * 100:.4f}".rstrip("0").rstrip(".")
    return numero.replace(".", ",") + "%"


def normalizar(texto: str) -> str:
    """Minúsculas y sin tildes, para comparar municipios y actividades."""
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    )
    return sin_tildes.strip().lower()


UVT_2026 = D("52374")
VERSION_TABLAS = "2026.1"
TABLA_UVT: dict[int, Decimal] = {2026: UVT_2026}

IVA_GENERAL = D("0.19")
IVA_DIFERENCIAL = D("0.05")
IVA_EXCLUIDO = D("0")
TARIFAS_IVA_PERMITIDAS = {IVA_GENERAL, IVA_DIFERENCIAL, IVA_EXCLUIDO}

TARIFA_RETEIVA = D("0.15")
MIN_RETEIVA_SERVICIOS_UVT = D("2")
MIN_RETEIVA_COMPRAS_UVT = D("10")


class TipoPersona(str, Enum):
    JURIDICA = "Jurídica"
    NATURAL = "Natural"


class Regimen(str, Enum):
    ORDINARIO = "Ordinario"
    SIMPLE = "SIMPLE"
    ESPECIAL = "Especial"


class TipoDocumento(str, Enum):
    FACTURA = "Factura electrónica"
    NOTA_CREDITO = "Nota crédito"
    DOCUMENTO_SOPORTE = "Documento soporte"


class Concepto(str, Enum):
    SERVICIO_GENERAL = "Servicio general"
    HONORARIOS = "Honorarios"
    ARRENDAMIENTO_VIVIENDA = "Arrendamiento de vivienda"
    ARRENDAMIENTO_MUEBLES = "Arrendamiento de bienes muebles"
    COMPRA_BIENES = "Compra de bienes"
    TRANSPORTE_CARGA = "Transporte de carga"
    HOTELES_RESTAURANTES = "Hoteles y restaurantes"


class Severidad(str, Enum):
    INFO = "Info"
    ALERTA = "Alerta"
    BLOQUEO = "Bloqueo"


@dataclass(frozen=True)
class Alerta:
    codigo: str
    mensaje: str
    severidad: Severidad = Severidad.ALERTA
    campo: str | None = None


class CalculoBloqueado(Exception):
    """El motor no calcula cuando falta un dato, una regla o el caso está fuera de alcance."""

    def __init__(self, mensaje: str, alertas: Sequence[Alerta] = ()) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.alertas = list(alertas)


class RevisionHumana(CalculoBloqueado):
    """Caso fuera del alcance de la v1: se deriva a revisión humana."""


class ReglaNoEncontrada(CalculoBloqueado):
    """No hay regla vigente para el concepto, la fecha o el municipio."""


@dataclass(frozen=True)
class Comprador:
    nit: str
    razon_social: str
    tipo: TipoPersona
    agente_retefuente: bool
    agente_reteiva: bool
    agente_reteica: bool
    municipio: str
    responsable_iva: bool
    obligado_contabilidad: bool
    regimen: Regimen = Regimen.ORDINARIO
    direccion: str = ""
    gran_contribuyente: bool = False
    entidad_estatal: bool = False
    emisor_tarjetas: bool = False


@dataclass(frozen=True)
class Proveedor:
    nit: str
    razon_social: str
    tipo: TipoPersona
    residente: bool
    declarante: bool
    responsable_iva: bool
    simple: bool
    autorretenedor: bool
    autorretencion_especial: bool
    gran_contribuyente: bool
    actividad_ciiu: str
    municipio: str
    rut_recibido: bool
    soporte_no_declarante: bool
    actividad_gravada_ica: bool = True


@dataclass(frozen=True)
class Operacion:
    tipo_documento: TipoDocumento
    numero: str
    fecha_emision: date
    fecha_pago: date
    concepto: Concepto
    descripcion: str
    base: Decimal | None
    tarifa_iva: Decimal
    iva: Decimal | None
    total: Decimal | None
    total_incluye_iva: bool
    descuentos: Decimal
    moneda: str
    trm: Decimal | None
    forma_pago: str
    valor_pagado: Decimal | None
    retencion_ya_practicada: bool
    factura_validada: bool
    orden_compra: bool
    acta_recibido: bool
    periodo_cerrado: bool
    iva_excluido: bool = False
    centro_costo: str = "ADMIN"


@dataclass(frozen=True)
class DatosFactura:
    base_bruta: Decimal
    descuentos: Decimal
    base: Decimal
    iva: Decimal
    total: Decimal
    tarifa_iva: Decimal
    moneda_original: str
    trm: Decimal
    factor_conversion: Decimal


@dataclass(frozen=True)
class ReglaRetefuente:
    id: str
    concepto: Concepto
    condicion: str
    tarifa: Decimal
    minimo_uvt: Decimal
    base: str
    fundamento: str
    vigencia_desde: date
    vigencia_hasta: date
    version: str = VERSION_TABLAS

    def vigente(self, fecha: date) -> bool:
        return self.vigencia_desde <= fecha <= self.vigencia_hasta


@dataclass(frozen=True)
class ReglaICA:
    municipio: str
    actividad: str
    tarifa: Decimal
    minimo_uvt: Decimal
    fundamento: str
    vigencia_desde: date
    vigencia_hasta: date
    version: str = VERSION_TABLAS

    def vigente(self, fecha: date) -> bool:
        return self.vigencia_desde <= fecha <= self.vigencia_hasta


@dataclass(frozen=True)
class FilaDecision:
    numero: int
    comprador: str
    proveedor: str
    concepto: Concepto
    aplica_rf: bool
    tarifa_rf: Decimal | None
    aplica_reteiva: str
    aplica_reteica: str


@dataclass
class LineaAsiento:
    cuenta: str
    nombre: str
    debito: Decimal
    credito: Decimal
    tercero: str
    centro_costo: str = ""
    descripcion: str = ""
    documento: str = ""


@dataclass
class Asiento:
    tipo: str
    fecha: date
    documento: str
    descripcion: str
    lineas: list[LineaAsiento] = field(default_factory=list)

    @property
    def total_debito(self) -> Decimal:
        return sum((linea.debito for linea in self.lineas), CERO)

    @property
    def total_credito(self) -> Decimal:
        return sum((linea.credito for linea in self.lineas), CERO)

    @property
    def diferencia(self) -> Decimal:
        return redondear(self.total_debito - self.total_credito)

    @property
    def cuadra(self) -> bool:
        return abs(self.diferencia) < D("0.005")


@dataclass
class CertificadoRetencion:
    tipo: str
    numero: str
    anio_gravable: int
    agente_nit: str
    agente_nombre: str
    retenido_nit: str
    retenido_nombre: str
    concepto: str
    base: Decimal
    tarifa: Decimal
    valor: Decimal
    fundamento: str
    ciudad: str
    fecha_expedicion: date
    base_sin_iva: Decimal | None = None
    iva: Decimal | None = None

    def validar(self) -> list[str]:
        faltantes: list[str] = []
        obligatorios = {
            "tipo": self.tipo,
            "número": self.numero,
            "NIT del agente": self.agente_nit,
            "nombre del agente": self.agente_nombre,
            "NIT del retenido": self.retenido_nit,
            "nombre del retenido": self.retenido_nombre,
            "concepto": self.concepto,
            "fundamento": self.fundamento,
            "ciudad": self.ciudad,
        }
        for nombre, valor in obligatorios.items():
            if valor is None or str(valor).strip() == "":
                faltantes.append(nombre)
        if self.base < 0 or self.valor < 0 or self.tarifa < 0:
            faltantes.append("valores negativos")
        if self.tipo == "ReteIVA" and (self.base_sin_iva is None or self.iva is None):
            faltantes.append("base sin IVA e IVA discriminados")
        return faltantes

    def requisitos_art_381(self) -> dict[str, Any]:
        """Los siete datos que debe explicar un certificado de renta."""
        return {
            "1. Nombre y NIT del agente retenedor": f"{self.agente_nombre} / {self.agente_nit}",
            "2. Nombre y NIT del retenido": f"{self.retenido_nombre} / {self.retenido_nit}",
            "3. Concepto": self.concepto,
            "4. Base": self.base,
            "5. Tarifa": self.tarifa,
            "6. Valor retenido": self.valor,
            "7. Año gravable": self.anio_gravable,
        }


@dataclass
class ItemChecklist:
    documento: str
    obligatorio: bool
    recibido: bool
    observacion: str = ""


@dataclass
class RegistroAuditoria:
    usuario: str
    fecha_hora: datetime
    version_tabla: str
    uvt: Decimal
    uvt_anio: int
    regla_id: str
    fundamento: str
    hash_entrada: str
    entrada_json: str
    resultado_json: str
    documentos: tuple[str, ...] = ()
    cambios: tuple[str, ...] = ()


@dataclass
class Liquidacion:
    comprador: Comprador
    proveedor: Proveedor
    operacion: Operacion
    datos: DatosFactura
    uvt: Decimal
    uvt_anio: int
    factor_pago: Decimal
    base_pago: Decimal
    iva_pago: Decimal
    total_pago: Decimal
    regla_rf: ReglaRetefuente | None
    tarifa_rf: Decimal
    base_rf: Decimal
    retefuente: Decimal
    minimo_rf_uvt: Decimal
    minimo_rf_valor: Decimal
    cumple_minimo_rf: bool
    aplica_reteiva: bool
    tarifa_reteiva: Decimal
    base_reteiva: Decimal
    reteiva: Decimal
    minimo_reteiva_uvt: Decimal
    minimo_reteiva_valor: Decimal
    cumple_minimo_reteiva: bool
    regla_ica: ReglaICA | None
    aplica_reteica: bool
    tarifa_reteica: Decimal
    base_reteica: Decimal
    reteica: Decimal
    minimo_reteica_uvt: Decimal
    minimo_reteica_valor: Decimal
    cumple_minimo_reteica: bool
    total_retenciones: Decimal
    neto: Decimal
    fila_decision: FilaDecision | None
    alertas: list[Alerta] = field(default_factory=list)
    asientos: list[Asiento] = field(default_factory=list)
    certificados: list[CertificadoRetencion] = field(default_factory=list)
    checklist: list[ItemChecklist] = field(default_factory=list)
    auditoria: RegistroAuditoria | None = None

    @property
    def asientos_cuadran(self) -> bool:
        return all(asiento.cuadra for asiento in self.asientos)

    @property
    def puede_pagar(self) -> bool:
        if any(a.severidad == Severidad.BLOQUEO for a in self.alertas):
            return False
        return all(item.recibido for item in self.checklist if item.obligatorio)

    def resumen(self) -> dict[str, Any]:
        return {
            "base_factura": self.datos.base,
            "iva_factura": self.datos.iva,
            "total_factura": self.datos.total,
            "factor_pago": self.factor_pago,
            "base_pago": self.base_pago,
            "iva_pago": self.iva_pago,
            "total_pago": self.total_pago,
            "concepto_rf": self.regla_rf.concepto.value if self.regla_rf else None,
            "regla_rf": self.regla_rf.id if self.regla_rf else None,
            "tarifa_rf": self.tarifa_rf,
            "base_rf": self.base_rf,
            "retefuente": self.retefuente,
            "aplica_reteiva": self.aplica_reteiva,
            "base_reteiva": self.base_reteiva,
            "reteiva": self.reteiva,
            "aplica_reteica": self.aplica_reteica,
            "base_reteica": self.base_reteica,
            "reteica": self.reteica,
            "total_retenciones": self.total_retenciones,
            "neto": self.neto,
            "fila_decision": self.fila_decision.numero if self.fila_decision else None,
            "uvt": self.uvt,
            "uvt_anio": self.uvt_anio,
            "version_tabla": VERSION_TABLAS,
            "asientos_cuadran": self.asientos_cuadran,
        }


def _regla_rf(
    id_: str,
    concepto: Concepto,
    condicion: str,
    tarifa: str,
    minimo_uvt: str,
    desde: date,
    hasta: date,
    fundamento: str,
) -> ReglaRetefuente:
    return ReglaRetefuente(
        id=id_,
        concepto=concepto,
        condicion=condicion,
        tarifa=D(tarifa),
        minimo_uvt=D(minimo_uvt),
        base="Valor antes de IVA, menos descuentos y devoluciones",
        fundamento=fundamento,
        vigencia_desde=desde,
        vigencia_hasta=hasta,
    )


_INICIO_2026 = date(2026, 1, 1)
_FIN_2026 = date(2026, 12, 31)
_CORTE_SUSPENSION = date(2026, 5, 7)
_INICIO_SUSPENSION = date(2026, 5, 8)
_FIN_SUSPENSION = date(2026, 6, 30)
_INICIO_D572 = date(2026, 7, 1)

TABLA_RETEFUENTE: tuple[ReglaRetefuente, ...] = (
    # Servicios generales: 4% declarante / 6% no declarante.
    # El mínimo cambia: 2 UVT, luego 4 UVT por la suspensión, y 2 UVT desde 1/07/2026.
    _regla_rf("RF-SERV-001", Concepto.SERVICIO_GENERAL, "declarante", "0.04", "2", _INICIO_2026, _CORTE_SUSPENSION, "Art. 392 ET; Decreto 572/2025; UVT 2026."),
    _regla_rf("RF-SERV-002", Concepto.SERVICIO_GENERAL, "no declarante", "0.06", "2", _INICIO_2026, _CORTE_SUSPENSION, "Art. 392 ET; Decreto 572/2025; UVT 2026."),
    _regla_rf("RF-SERV-003", Concepto.SERVICIO_GENERAL, "declarante", "0.04", "4", _INICIO_SUSPENSION, _FIN_SUSPENSION, "Suspensión temporal de los arts. 2–8 del Decreto 572/2025; UVT 2026."),
    _regla_rf("RF-SERV-004", Concepto.SERVICIO_GENERAL, "no declarante", "0.06", "4", _INICIO_SUSPENSION, _FIN_SUSPENSION, "Suspensión temporal de los arts. 2–8 del Decreto 572/2025; UVT 2026."),
    _regla_rf("RF-SERV-005", Concepto.SERVICIO_GENERAL, "declarante", "0.04", "2", _INICIO_D572, _FIN_2026, "Art. 392 ET; Decreto 572/2025; efectos desde 1/07/2026; UVT 2026."),
    _regla_rf("RF-SERV-006", Concepto.SERVICIO_GENERAL, "no declarante", "0.06", "2", _INICIO_D572, _FIN_2026, "Art. 392 ET; Decreto 572/2025; efectos desde 1/07/2026; UVT 2026."),
    # Honorarios: sin mínimo de retefuente.
    _regla_rf("RF-HON-001", Concepto.HONORARIOS, "declarante", "0.11", "0", _INICIO_2026, _FIN_2026, "Art. 392 ET; Art. 383 ET (excepción de 3.300 UVT)."),
    _regla_rf("RF-HON-002", Concepto.HONORARIOS, "no declarante", "0.10", "0", _INICIO_2026, _FIN_2026, "Art. 392 ET; Art. 383 ET (excepción de 3.300 UVT)."),
    # Arrendamiento de vivienda: 3,5%, mínimo 10 UVT; IVA excluido.
    _regla_rf("RF-ARR-001", Concepto.ARRENDAMIENTO_VIVIENDA, "declarante", "0.035", "10", _INICIO_2026, _FIN_2026, "Art. 392 ET; Art. 387 ET; UVT 2026."),
    _regla_rf("RF-ARR-002", Concepto.ARRENDAMIENTO_VIVIENDA, "no declarante", "0.035", "10", _INICIO_2026, _FIN_2026, "Art. 392 ET; Art. 387 ET; UVT 2026."),
    # Arrendamiento de bienes muebles: 4%, sin mínimo.
    _regla_rf("RF-ARRM-001", Concepto.ARRENDAMIENTO_MUEBLES, "declarante", "0.04", "0", _INICIO_2026, _FIN_2026, "Art. 392 ET; UVT 2026."),
    _regla_rf("RF-ARRM-002", Concepto.ARRENDAMIENTO_MUEBLES, "no declarante", "0.04", "0", _INICIO_2026, _FIN_2026, "Art. 392 ET; UVT 2026."),
    # Compras generales: 2,5% declarante / 3,5% no declarante; mínimo 10 UVT.
    _regla_rf("RF-COMP-001", Concepto.COMPRA_BIENES, "declarante", "0.025", "10", _INICIO_2026, _FIN_2026, "Art. 392 ET; Art. 401 ET; UVT 2026."),
    _regla_rf("RF-COMP-002", Concepto.COMPRA_BIENES, "no declarante", "0.035", "10", _INICIO_2026, _FIN_2026, "Art. 392 ET; Art. 401 ET; UVT 2026."),
    # Conceptos adicionales de la tabla de referencia.
    _regla_rf("RF-TRAN-001", Concepto.TRANSPORTE_CARGA, "declarante", "0.01", "2", _INICIO_2026, _FIN_2026, "Art. 392 ET; UVT 2026."),
    _regla_rf("RF-TRAN-002", Concepto.TRANSPORTE_CARGA, "no declarante", "0.01", "2", _INICIO_2026, _FIN_2026, "Art. 392 ET; UVT 2026."),
    _regla_rf("RF-HOT-001", Concepto.HOTELES_RESTAURANTES, "declarante", "0.035", "2", _INICIO_2026, _FIN_2026, "Art. 392 ET; UVT 2026."),
    _regla_rf("RF-HOT-002", Concepto.HOTELES_RESTAURANTES, "no declarante", "0.035", "2", _INICIO_2026, _FIN_2026, "Art. 392 ET; UVT 2026."),
)

TABLA_ICA: tuple[ReglaICA, ...] = (
    ReglaICA(
        municipio="Bogotá",
        actividad="Servicios",
        tarifa=D("0.00966"),
        minimo_uvt=D("0"),
        fundamento="Acuerdo 724 de 2026 (tarifa pedagógica; mínimo no configurado; verificar actividad y vigencia).",
        vigencia_desde=_INICIO_2026,
        vigencia_hasta=_FIN_2026,
    ),
)


def buscar_regla_retefuente(
    concepto: Concepto,
    declarante: bool,
    fecha: date,
    tabla: Sequence[ReglaRetefuente] = TABLA_RETEFUENTE,
) -> ReglaRetefuente:
    condicion = "declarante" if declarante else "no declarante"
    candidatas = [
        regla
        for regla in tabla
        if regla.concepto == concepto and regla.condicion == condicion and regla.vigente(fecha)
    ]
    if not candidatas:
        raise ReglaNoEncontrada(
            f"No hay regla de retefuente vigente para {concepto.value!r} "
            f"({condicion}) el {fecha.isoformat()}."
        )
    return max(candidatas, key=lambda r: r.vigencia_desde)


def buscar_regla_ica(
    municipio: str,
    actividad: str,
    fecha: date,
    tabla: Sequence[ReglaICA] = TABLA_ICA,
) -> ReglaICA | None:
    municipio_n = normalizar(municipio)
    actividad_n = normalizar(actividad)
    candidatas = [
        regla
        for regla in tabla
        if normalizar(regla.municipio) == municipio_n
        and normalizar(regla.actividad) == actividad_n
        and regla.vigente(fecha)
    ]
    if not candidatas:
        return None
    return max(candidatas, key=lambda r: r.vigencia_desde)


def categoria_reteiva(concepto: Concepto) -> str:
    return "compra" if concepto == Concepto.COMPRA_BIENES else "servicio"


def categoria_ica(concepto: Concepto) -> str:
    return "Compras" if concepto == Concepto.COMPRA_BIENES else "Servicios"


def minimo_reteiva_uvt(concepto: Concepto) -> Decimal:
    return MIN_RETEIVA_COMPRAS_UVT if categoria_reteiva(concepto) == "compra" else MIN_RETEIVA_SERVICIOS_UVT


def _fila(
    numero: int,
    comprador: str,
    proveedor: str,
    concepto: Concepto,
    aplica_rf: bool,
    tarifa_rf: str | None,
    aplica_reteiva: str,
    aplica_reteica: str,
) -> FilaDecision:
    return FilaDecision(
        numero=numero,
        comprador=comprador,
        proveedor=proveedor,
        concepto=concepto,
        aplica_rf=aplica_rf,
        tarifa_rf=D(tarifa_rf) if tarifa_rf is not None else None,
        aplica_reteiva=aplica_reteiva,
        aplica_reteica=aplica_reteica,
    )


TABLA_DECISION: tuple[FilaDecision, ...] = (
    _fila(1, "Agente RF, no reteIVA, no reteICA", "Declarante", Concepto.SERVICIO_GENERAL, True, "0.04", "No", "No"),
    _fila(2, "Agente RF, no reteIVA, no reteICA", "No declarante", Concepto.SERVICIO_GENERAL, True, "0.06", "No", "No"),
    _fila(3, "Agente RF, no reteIVA, no reteICA", "Declarante", Concepto.HONORARIOS, True, "0.11", "No", "No"),
    _fila(4, "Agente RF, no reteIVA, no reteICA", "No declarante", Concepto.HONORARIOS, True, "0.10", "No", "No"),
    _fila(5, "Agente RF, no reteIVA, no reteICA", "Declarante", Concepto.ARRENDAMIENTO_VIVIENDA, True, "0.035", "No", "No"),
    _fila(6, "Agente RF, no reteIVA, no reteICA", "Declarante", Concepto.COMPRA_BIENES, True, "0.025", "No", "No"),
    _fila(7, "Agente RF, no reteIVA, no reteICA", "No declarante", Concepto.COMPRA_BIENES, True, "0.035", "No", "No"),
    _fila(8, "Agente RF y reteIVA", "Declarante", Concepto.SERVICIO_GENERAL, True, "0.04", "15%", "No"),
    _fila(9, "Agente RF y reteIVA", "Declarante", Concepto.COMPRA_BIENES, True, "0.025", "15%", "No"),
    _fila(10, "Agente RF y reteICA", "Declarante", Concepto.SERVICIO_GENERAL, True, "0.04", "No", "Tarifa municipal"),
    _fila(11, "Agente RF, reteIVA y reteICA", "Declarante", Concepto.SERVICIO_GENERAL, True, "0.04", "15%", "Tarifa municipal"),
    _fila(12, "Agente RF", "SIMPLE", Concepto.SERVICIO_GENERAL, False, "0", "15% si es responsable de IVA", "0%"),
    _fila(13, "Agente RF", "Autorretenedor", Concepto.SERVICIO_GENERAL, False, "0", "15% si aplica", "Según municipio"),
    _fila(14, "No agente RF", "Cualquiera", Concepto.SERVICIO_GENERAL, False, "0", "Según agente", "Según agente"),
)


def buscar_fila_decision(
    comprador: Comprador,
    proveedor: Proveedor,
    concepto: Concepto,
) -> FilaDecision | None:
    """Devuelve la fila pedagógica que mejor describe la combinación.

    La tabla es pedagógica y no cubre todas las combinaciones (por ejemplo,
    honorarios con comprador agente de reteIVA). Si no hay coincidencia, el
    motor sigue calculando con las reglas y deja la fila en ``None``.
    """
    if not comprador.agente_retefuente:
        return next(f for f in TABLA_DECISION if f.numero == 14)
    if proveedor.simple:
        return next(f for f in TABLA_DECISION if f.numero == 12)
    if proveedor.autorretenedor:
        return next(f for f in TABLA_DECISION if f.numero == 13)

    if concepto == Concepto.SERVICIO_GENERAL:
        if comprador.agente_reteiva and comprador.agente_reteica:
            return next(f for f in TABLA_DECISION if f.numero == 11)
        if comprador.agente_reteiva:
            return next(f for f in TABLA_DECISION if f.numero == 8)
        if comprador.agente_reteica:
            return next(f for f in TABLA_DECISION if f.numero == 10)
        return next(f for f in TABLA_DECISION if f.numero == (1 if proveedor.declarante else 2))

    if concepto == Concepto.HONORARIOS:
        if comprador.agente_reteiva or comprador.agente_reteica:
            return None
        return next(f for f in TABLA_DECISION if f.numero == (3 if proveedor.declarante else 4))
    if concepto == Concepto.ARRENDAMIENTO_VIVIENDA:
        if comprador.agente_reteica:
            return None
        return next(f for f in TABLA_DECISION if f.numero == 5)
    if concepto == Concepto.COMPRA_BIENES:
        if comprador.agente_reteica:
            return None
        if comprador.agente_reteiva:
            return next(f for f in TABLA_DECISION if f.numero == 9)
        return next(f for f in TABLA_DECISION if f.numero == (6 if proveedor.declarante else 7))
    return None


CUENTAS = {
    "servicios": ("5135", "Servicios"),
    "honorarios": ("5110", "Honorarios"),
    "arrendamientos": ("5120", "Arrendamientos"),
    "inventarios": ("143505", "Inventarios"),
    "iva_descontable": ("240805", "IVA descontable"),
    "proveedores": ("220505", "Proveedores nacionales"),
    "bancos": ("111005", "Bancos"),
    "rf_servicios": ("236525", "Retención en la fuente — servicios"),
    "rf_honorarios": ("236515", "Retención en la fuente — honorarios"),
    "rf_arrendamientos": ("236530", "Retención en la fuente — arrendamientos"),
    "rf_compras": ("236540", "Retención en la fuente — compras"),
    "reteiva": ("236701", "Impuesto a las ventas retenido"),
    "reteica": ("2368", "Impuesto de industria y comercio retenido"),
}


def cuenta_gasto(concepto: Concepto) -> tuple[str, str]:
    if concepto == Concepto.HONORARIOS:
        return CUENTAS["honorarios"]
    if concepto in (Concepto.ARRENDAMIENTO_VIVIENDA, Concepto.ARRENDAMIENTO_MUEBLES):
        return CUENTAS["arrendamientos"]
    if concepto == Concepto.COMPRA_BIENES:
        return CUENTAS["inventarios"]
    return CUENTAS["servicios"]


def cuenta_retefuente(concepto: Concepto) -> tuple[str, str]:
    if concepto == Concepto.HONORARIOS:
        return CUENTAS["rf_honorarios"]
    if concepto in (Concepto.ARRENDAMIENTO_VIVIENDA, Concepto.ARRENDAMIENTO_MUEBLES):
        return CUENTAS["rf_arrendamientos"]
    if concepto == Concepto.COMPRA_BIENES:
        return CUENTAS["rf_compras"]
    return CUENTAS["rf_servicios"]


def normalizar_factura(operacion: Operacion) -> DatosFactura:
    moneda = operacion.moneda.upper().strip()
    if moneda == "COP":
        factor = D("1")
        trm = D("1")
    elif moneda == "USD":
        if operacion.trm is None or D(operacion.trm) <= 0:
            raise CalculoBloqueado("Si la moneda es USD, la TRM debe ser mayor que cero.")
        trm = D(operacion.trm)
        factor = trm
    else:
        raise CalculoBloqueado(f"Moneda no soportada: {operacion.moneda!r}. Use COP o USD.")

    tarifa = D(operacion.tarifa_iva)
    if operacion.iva_excluido and tarifa != IVA_EXCLUIDO:
        raise CalculoBloqueado("La operación está marcada como IVA excluido, pero la tarifa no es 0%.")

    base_ingresada = D(operacion.base) * factor if operacion.base is not None else None
    iva_ingresado = D(operacion.iva) * factor if operacion.iva is not None else None
    total_ingresado = D(operacion.total) * factor if operacion.total is not None else None
    descuentos = D(operacion.descuentos) * factor

    if descuentos < 0:
        raise CalculoBloqueado("Los descuentos no pueden ser negativos.")

    if operacion.total_incluye_iva:
        if total_ingresado is None:
            raise CalculoBloqueado("Si el total incluye IVA, debe informar el total.")
        if total_ingresado <= 0:
            raise CalculoBloqueado("El total debe ser mayor que cero.")
        base = dinero(total_ingresado / (D("1") + tarifa))
        iva = dinero(total_ingresado - base)
        if base_ingresada is not None:
            base_declarada = base_ingresada - descuentos
            if abs(base_declarada - base) > CENTAVO:
                raise CalculoBloqueado(
                    "La base informada no coincide con la base implícita en el total con IVA."
                )
        if iva_ingresado is not None and abs(iva_ingresado - iva) > CENTAVO:
            raise CalculoBloqueado(
                "El IVA informado no coincide con el IVA implícito en el total con IVA."
            )
        base_bruta = dinero(base + descuentos)
        total = dinero(total_ingresado)
    else:
        if base_ingresada is None:
            if total_ingresado is not None and iva_ingresado is not None:
                base = dinero(total_ingresado - iva_ingresado)
            elif total_ingresado is not None and tarifa == IVA_EXCLUIDO:
                base = dinero(total_ingresado)
            else:
                raise CalculoBloqueado(
                    "Falta la base. Informe base, o total e IVA, para poder liquidar."
                )
            base_bruta = dinero(base + descuentos)
        else:
            base = dinero(base_ingresada - descuentos)
            base_bruta = dinero(base_ingresada)

        if base <= 0:
            raise CalculoBloqueado("La base después de descuentos debe ser mayor que cero.")

        iva = dinero(iva_ingresado) if iva_ingresado is not None else dinero(base * tarifa)
        total = dinero(total_ingresado) if total_ingresado is not None else dinero(base + iva)

        if iva < 0:
            raise CalculoBloqueado("El IVA no puede ser negativo.")
        if abs(dinero(base + iva) - total) > CENTAVO:
            raise CalculoBloqueado(
                f"El total no cuadra: base {cop(base)} + IVA {cop(iva)} = {cop(base + iva)}, "
                f"pero el total informado es {cop(total)}."
            )

    if base <= 0:
        raise CalculoBloqueado("La base debe ser mayor que cero.")
    if descuentos > base_bruta:
        raise CalculoBloqueado("Los descuentos no pueden superar la base bruta.")

    return DatosFactura(
        base_bruta=dinero(base_bruta),
        descuentos=dinero(descuentos),
        base=dinero(base),
        iva=dinero(iva),
        total=dinero(total),
        tarifa_iva=tarifa,
        moneda_original=moneda,
        trm=trm,
        factor_conversion=factor,
    )


def _alerta(codigo: str, mensaje: str, severidad: Severidad = Severidad.ALERTA, campo: str | None = None) -> Alerta:
    return Alerta(codigo=codigo, mensaje=mensaje, severidad=severidad, campo=campo)


def _exigir_sin_bloqueos(alertas: Sequence[Alerta]) -> None:
    bloqueos = [a for a in alertas if a.severidad == Severidad.BLOQUEO]
    if bloqueos:
        raise CalculoBloqueado(
            "No se puede liquidar: " + " | ".join(a.mensaje for a in bloqueos),
            alertas,
        )


def validar_entradas(comprador: Comprador, proveedor: Proveedor, operacion: Operacion) -> list[Alerta]:
    alertas: list[Alerta] = []

    if not comprador.nit.strip():
        alertas.append(_alerta("COMP-NIT", "El comprador no tiene NIT.", Severidad.BLOQUEO, "comprador.nit"))
    if not comprador.razon_social.strip():
        alertas.append(_alerta("COMP-NOMBRE", "El comprador no tiene razón social.", Severidad.BLOQUEO, "comprador.razon_social"))
    if not proveedor.nit.strip():
        alertas.append(_alerta("PROV-NIT", "El proveedor no está identificado: falta el NIT.", Severidad.BLOQUEO, "proveedor.nit"))
    if not proveedor.razon_social.strip():
        alertas.append(_alerta("PROV-NOMBRE", "El proveedor no tiene razón social.", Severidad.BLOQUEO, "proveedor.razon_social"))
    if not operacion.numero.strip():
        alertas.append(_alerta("OP-NUMERO", "La operación no tiene número de documento.", Severidad.BLOQUEO, "operacion.numero"))
    if operacion.fecha_pago < operacion.fecha_emision:
        alertas.append(_alerta("OP-FECHAS", "La fecha de pago no puede ser anterior a la fecha de emisión.", Severidad.BLOQUEO, "operacion.fecha_pago"))
    if operacion.fecha_emision.year != operacion.fecha_pago.year:
        alertas.append(_alerta("OP-ANIO", "La operación cruza año: revise la UVT y la vigencia aplicable.", Severidad.BLOQUEO, "operacion.fecha_pago"))
    if D(operacion.tarifa_iva) not in TARIFAS_IVA_PERMITIDAS:
        alertas.append(_alerta("IVA-TARIFA", f"Tarifa de IVA no permitida: {porcentaje(operacion.tarifa_iva)}.", Severidad.BLOQUEO, "operacion.tarifa_iva"))
    if operacion.tipo_documento == TipoDocumento.NOTA_CREDITO:
        alertas.append(_alerta("OP-NC", "La nota crédito se procesa con el módulo de ajustes, no como factura.", Severidad.BLOQUEO, "operacion.tipo_documento"))

    if not proveedor.residente:
        alertas.append(_alerta("PROV-EXTERIOR", "Proveedor no residente: el caso se deriva al módulo de pagos al exterior (fuera de la v1).", Severidad.BLOQUEO, "proveedor.residente"))
    if not comprador.obligado_contabilidad:
        alertas.append(_alerta("COMP-CONTABILIDAD", "El comprador no está obligado a llevar contabilidad; la v1 no cubre ese caso.", Severidad.BLOQUEO, "comprador.obligado_contabilidad"))
    if comprador.regimen == Regimen.SIMPLE:
        alertas.append(_alerta("COMP-SIMPLE", "La v1 no cubre compradores del régimen SIMPLE.", Severidad.BLOQUEO, "comprador.regimen"))
    if comprador.gran_contribuyente and proveedor.gran_contribuyente:
        alertas.append(_alerta("RETEIVA-GC", "Operación entre grandes contribuyentes: posible exclusión de reteIVA; requiere revisión humana.", Severidad.BLOQUEO, "proveedor.gran_contribuyente"))
    if proveedor.autorretencion_especial and not proveedor.autorretenedor:
        alertas.append(_alerta("AUTORRET-ESPECIAL", "El proveedor solo tiene autorretención especial (código 59). No se asume exención de la retención general: revisión humana.", Severidad.BLOQUEO, "proveedor.autorretencion_especial"))
    if proveedor.tipo == TipoPersona.JURIDICA and not proveedor.declarante and not proveedor.simple:
        alertas.append(_alerta("PROV-DECLARANTE", "Una persona jurídica debe ser declarante de renta; revise el RUT del proveedor.", Severidad.BLOQUEO, "proveedor.declarante"))
    if not proveedor.declarante and not proveedor.simple and not proveedor.soporte_no_declarante:
        alertas.append(_alerta("PROV-SOPORTE", "No hay certificación de no declarante. Use la tarifa conservadora o bloquee; la v1 bloquea.", Severidad.BLOQUEO, "proveedor.soporte_no_declarante"))
    if not proveedor.rut_recibido:
        alertas.append(_alerta("PROV-RUT", "Falta el RUT del proveedor: no se puede autorizar el pago.", Severidad.ALERTA, "proveedor.rut_recibido"))
    if not operacion.factura_validada:
        alertas.append(_alerta("DOC-FACTURA", "La factura no está validada por la DIAN: se bloquea el IVA y el costo.", Severidad.BLOQUEO, "operacion.factura_validada"))
    if operacion.periodo_cerrado:
        alertas.append(_alerta("PERIODO-CERRADO", "El periodo está cerrado; se requiere un ajuste autorizado.", Severidad.BLOQUEO, "operacion.periodo_cerrado"))
    if operacion.retencion_ya_practicada:
        alertas.append(_alerta("RETENCION-DUP", "La retención ya fue practicada; no se permite un segundo cálculo sin autorización.", Severidad.BLOQUEO, "operacion.retencion_ya_practicada"))
    if not operacion.descripcion.strip():
        alertas.append(_alerta("OP-DESCRIPCION", "Falta la descripción de la operación.", Severidad.ALERTA, "operacion.descripcion"))
    if comprador.municipio.strip() == "" and comprador.agente_reteica:
        alertas.append(_alerta("COMP-MUNICIPIO", "El comprador es agente de reteICA pero no tiene municipio.", Severidad.BLOQUEO, "comprador.municipio"))

    return alertas


def _validar_valor_pagado(operacion: Operacion, total: Decimal) -> None:
    if operacion.valor_pagado is None:
        return
    valor = D(operacion.valor_pagado)
    if valor <= 0:
        raise CalculoBloqueado("El valor pagado debe ser mayor que cero.")
    if valor > total + CENTAVO:
        raise CalculoBloqueado("El valor pagado no puede superar el total de la factura.")


class RepositorioFacturas:
    """Memoria mínima para detectar duplicados por proveedor + número."""

    def __init__(self) -> None:
        self._facturas: set[tuple[str, str]] = set()

    def existe(self, proveedor_nit: str, numero: str) -> bool:
        return (normalizar(proveedor_nit), normalizar(numero)) in self._facturas

    def registrar(self, proveedor_nit: str, numero: str) -> None:
        self._facturas.add((normalizar(proveedor_nit), normalizar(numero)))


class LiquidadorRetenciones:
    """Motor que aplica las reglas del diseño funcional."""

    def __init__(
        self,
        usuario: str = "usuario.demo",
        repositorio: RepositorioFacturas | None = None,
        tabla_uvt: dict[int, Decimal] | None = None,
        tabla_retefuente: Sequence[ReglaRetefuente] | None = None,
        tabla_ica: Sequence[ReglaICA] | None = None,
    ) -> None:
        self.usuario = usuario
        self.repositorio = repositorio
        self.tabla_uvt = tabla_uvt or TABLA_UVT
        self.tabla_retefuente = tuple(tabla_retefuente or TABLA_RETEFUENTE)
        self.tabla_ica = tuple(tabla_ica or TABLA_ICA)

    def _uvt(self, fecha: date) -> tuple[Decimal, int]:
        if fecha.year not in self.tabla_uvt:
            raise ReglaNoEncontrada(f"No hay UVT cargada para el año {fecha.year}.")
        return self.tabla_uvt[fecha.year], fecha.year

    def calcular(
        self,
        comprador: Comprador,
        proveedor: Proveedor,
        operacion: Operacion,
        autorizar_duplicado: bool = False,
    ) -> Liquidacion:
        alertas = validar_entradas(comprador, proveedor, operacion)
        _exigir_sin_bloqueos(alertas)

        if self.repositorio and self.repositorio.existe(proveedor.nit, operacion.numero) and not autorizar_duplicado:
            raise CalculoBloqueado(
                f"Posible factura duplicada: ya existe {operacion.numero} del proveedor {proveedor.nit}."
            )

        datos = normalizar_factura(operacion)
        if datos.moneda_original == "USD":
            alertas.append(
                _alerta(
                    "MONEDA-USD",
                    f"Conversión simple a COP con TRM {datos.trm}. No incluye diferencia en cambio.",
                    Severidad.INFO,
                    "operacion.trm",
                )
            )

        uvt, uvt_anio = self._uvt(operacion.fecha_emision)
        _validar_valor_pagado(operacion, datos.total)

        # Pago total o parcial. Las retenciones se calculan sobre la parte pagada.
        if operacion.valor_pagado is None:
            factor_pago = D("1")
            total_pago = datos.total
        else:
            total_pago = dinero(operacion.valor_pagado)
            factor_pago = total_pago / datos.total
            if factor_pago < 1:
                alertas.append(
                    _alerta(
                        "PAGO-PARCIAL",
                        "Pago parcial: las retenciones se calculan sobre la parte pagada, no sobre la factura completa.",
                        Severidad.INFO,
                        "operacion.valor_pagado",
                    )
                )

        base_pago = dinero(datos.base * factor_pago)
        iva_pago = dinero(datos.iva * factor_pago)

        # --- Retefuente (renta) ---
        regla_rf: ReglaRetefuente | None = None
        tarifa_rf = CERO
        base_rf = base_pago
        retefuente = CERO
        minimo_rf_uvt = CERO
        minimo_rf_valor = CERO
        cumple_minimo_rf = True

        if not comprador.agente_retefuente:
            alertas.append(_alerta("RF-AGENTE", "El comprador no es agente de retefuente; no se practica retefuente.", Severidad.INFO))
        elif proveedor.simple:
            alertas.append(_alerta("RF-SIMPLE", "Proveedor SIMPLE: no se practica retefuente (Art. 911 ET).", Severidad.INFO))
        elif proveedor.autorretenedor:
            alertas.append(_alerta("RF-AUTORRET", "Proveedor autorretenedor: el comprador no practica retefuente.", Severidad.INFO))
        else:
            regla_rf = buscar_regla_retefuente(
                operacion.concepto,
                proveedor.declarante,
                operacion.fecha_emision,
                self.tabla_retefuente,
            )
            minimo_rf_uvt = regla_rf.minimo_uvt
            minimo_rf_valor = dinero(minimo_rf_uvt * uvt)
            cumple_minimo_rf = base_pago >= minimo_rf_valor
            if not cumple_minimo_rf:
                alertas.append(
                    _alerta(
                        "RF-MINIMO",
                        f"La base {cop(base_pago)} es inferior al mínimo de {minimo_rf_uvt} UVT "
                        f"({cop(minimo_rf_valor)}); no se practica retefuente.",
                        Severidad.INFO,
                    )
                )
            else:
                tarifa_rf = regla_rf.tarifa
                retefuente = dinero(base_pago * tarifa_rf)

        # --- ReteIVA ---
        aplica_reteiva = False
        tarifa_reteiva = TARIFA_RETEIVA
        base_reteiva = iva_pago
        reteiva = CERO
        min_riva_uvt = minimo_reteiva_uvt(operacion.concepto)
        min_riva_valor = dinero(min_riva_uvt * uvt)
        cumple_minimo_reteiva = iva_pago > 0 and base_pago >= min_riva_valor

        if not comprador.agente_reteiva:
            alertas.append(_alerta("RIVA-AGENTE", "El comprador no es agente de reteIVA; no se practica reteIVA.", Severidad.INFO))
        elif not proveedor.responsable_iva:
            alertas.append(_alerta("RIVA-RESPONSABLE", "El proveedor no es responsable de IVA; no se practica reteIVA.", Severidad.INFO))
        elif iva_pago <= 0:
            alertas.append(_alerta("RIVA-SIN-IVA", "La operación no tiene IVA; no se practica reteIVA.", Severidad.INFO))
        elif not cumple_minimo_reteiva:
            alertas.append(
                _alerta(
                    "RIVA-MINIMO",
                    f"La base {cop(base_pago)} no supera el mínimo de reteIVA de {min_riva_uvt} UVT "
                    f"({cop(min_riva_valor)}); no se practica reteIVA.",
                    Severidad.INFO,
                )
            )
        else:
            aplica_reteiva = True
            reteiva = dinero(iva_pago * tarifa_reteiva)

        # --- ReteICA ---
        aplica_reteica = False
        regla_ica: ReglaICA | None = None
        tarifa_reteica = CERO
        base_reteica = base_pago
        reteica = CERO
        minimo_reteica_uvt = CERO
        minimo_reteica_valor = CERO
        cumple_minimo_reteica = True

        if not comprador.agente_reteica:
            alertas.append(_alerta("RICA-AGENTE", "El comprador no es agente de reteICA; no se practica reteICA.", Severidad.INFO))
        elif proveedor.simple:
            alertas.append(_alerta("RICA-SIMPLE", "Proveedor SIMPLE: no se practica reteICA.", Severidad.INFO))
        elif not proveedor.actividad_gravada_ica:
            alertas.append(_alerta("RICA-ACTIVIDAD", "La actividad del proveedor no está gravada en ICA; no se practica reteICA.", Severidad.INFO))
        else:
            regla_ica = buscar_regla_ica(
                comprador.municipio,
                categoria_ica(operacion.concepto),
                operacion.fecha_emision,
                self.tabla_ica,
            )
            if regla_ica is None:
                raise ReglaNoEncontrada(
                    f"No hay tarifa de reteICA para {comprador.municipio!r}, "
                    f"actividad {categoria_ica(operacion.concepto)!r}, el {operacion.fecha_emision.isoformat()}. "
                    "No se inventa la tarifa."
                )
            minimo_reteica_uvt = regla_ica.minimo_uvt
            minimo_reteica_valor = dinero(minimo_reteica_uvt * uvt)
            cumple_minimo_reteica = base_pago >= minimo_reteica_valor
            if not cumple_minimo_reteica:
                alertas.append(
                    _alerta(
                        "RICA-MINIMO",
                        f"La base {cop(base_pago)} es inferior al mínimo municipal de "
                        f"{minimo_reteica_uvt} UVT ({cop(minimo_reteica_valor)}); no se practica reteICA.",
                        Severidad.INFO,
                    )
                )
            else:
                aplica_reteica = True
                tarifa_reteica = regla_ica.tarifa
                reteica = dinero(base_pago * tarifa_reteica)

        total_retenciones = dinero(retefuente + reteiva + reteica)
        neto = dinero(total_pago - total_retenciones)
        if neto < 0:
            raise CalculoBloqueado(
                f"El neto a pagar sería negativo ({cop(neto)}). Revise las retenciones y el valor pagado."
            )

        if not proveedor.declarante and not proveedor.simple and proveedor.rut_recibido:
            alertas.append(_alerta("PROV-NO-DECL", "Proveedor no declarante: conserve la certificación y el RUT en el expediente.", Severidad.INFO))

        fila_decision = buscar_fila_decision(comprador, proveedor, operacion.concepto)
        if fila_decision is None:
            alertas.append(_alerta("DECISION-NO-TABULADA", "La combinación no está en la tabla pedagógica; se aplicaron las reglas por concepto.", Severidad.INFO))

        liquidacion = Liquidacion(
            comprador=comprador,
            proveedor=proveedor,
            operacion=operacion,
            datos=datos,
            uvt=uvt,
            uvt_anio=uvt_anio,
            factor_pago=factor_pago,
            base_pago=base_pago,
            iva_pago=iva_pago,
            total_pago=total_pago,
            regla_rf=regla_rf,
            tarifa_rf=tarifa_rf,
            base_rf=base_rf,
            retefuente=retefuente,
            minimo_rf_uvt=minimo_rf_uvt,
            minimo_rf_valor=minimo_rf_valor,
            cumple_minimo_rf=cumple_minimo_rf,
            aplica_reteiva=aplica_reteiva,
            tarifa_reteiva=tarifa_reteiva,
            base_reteiva=base_reteiva,
            reteiva=reteiva,
            minimo_reteiva_uvt=min_riva_uvt,
            minimo_reteiva_valor=min_riva_valor,
            cumple_minimo_reteiva=cumple_minimo_reteiva,
            regla_ica=regla_ica,
            aplica_reteica=aplica_reteica,
            tarifa_reteica=tarifa_reteica,
            base_reteica=base_reteica,
            reteica=reteica,
            minimo_reteica_uvt=minimo_reteica_uvt,
            minimo_reteica_valor=minimo_reteica_valor,
            cumple_minimo_reteica=cumple_minimo_reteica,
            total_retenciones=total_retenciones,
            neto=neto,
            fila_decision=fila_decision,
            alertas=alertas,
        )

        liquidacion.asientos = self._crear_asientos(liquidacion)
        liquidacion.certificados = self._crear_certificados(liquidacion)
        liquidacion.checklist = self._crear_checklist(liquidacion)
        liquidacion.auditoria = self._crear_auditoria(liquidacion)

        if not liquidacion.asientos_cuadran:
            raise CalculoBloqueado("El asiento no cuadra: débitos ≠ créditos. No se permite guardar.")

        if self.repositorio:
            self.repositorio.registrar(proveedor.nit, operacion.numero)

        return liquidacion

    # ------------------------------------------------------------------
    # Asientos
    # ------------------------------------------------------------------
    def _crear_asientos(self, liq: Liquidacion) -> list[Asiento]:
        op = liq.operacion
        tercero = f"{liq.proveedor.razon_social} / {liq.proveedor.nit}"
        documento = op.numero
        asientos: list[Asiento] = []

        # 1) Causación: gasto/inventario + IVA descontable contra proveedores.
        cuenta, nombre_cuenta = cuenta_gasto(op.concepto)
        lineas_causacion: list[LineaAsiento] = []
        if liq.comprador.responsable_iva and liq.datos.iva > 0:
            lineas_causacion.append(
                LineaAsiento(cuenta, nombre_cuenta, liq.datos.base, CERO, tercero, op.centro_costo, op.descripcion, documento)
            )
            lineas_causacion.append(
                LineaAsiento(
                    CUENTAS["iva_descontable"][0],
                    CUENTAS["iva_descontable"][1],
                    liq.datos.iva,
                    CERO,
                    tercero,
                    op.centro_costo,
                    "IVA descontable de la factura",
                    documento,
                )
            )
        else:
            lineas_causacion.append(
                LineaAsiento(cuenta, nombre_cuenta, liq.datos.total, CERO, tercero, op.centro_costo, op.descripcion, documento)
            )
        lineas_causacion.append(
            LineaAsiento(
                CUENTAS["proveedores"][0],
                CUENTAS["proveedores"][1],
                CERO,
                liq.datos.total,
                tercero,
                op.centro_costo,
                "Proveedor nacional",
                documento,
            )
        )
        asientos.append(Asiento("Causación", op.fecha_emision, documento, "Causación de la factura", lineas_causacion))

        # 2) Pago: proveedores contra banco y retenciones.
        lineas_pago: list[LineaAsiento] = [
            LineaAsiento(
                CUENTAS["proveedores"][0],
                CUENTAS["proveedores"][1],
                liq.total_pago,
                CERO,
                tercero,
                op.centro_costo,
                "Pago total o parcial de la factura",
                documento,
            ),
            LineaAsiento(
                CUENTAS["bancos"][0],
                CUENTAS["bancos"][1],
                CERO,
                liq.neto,
                tercero,
                op.centro_costo,
                "Salida de bancos",
                documento,
            ),
        ]
        if liq.retefuente > 0:
            cta, nom = cuenta_retefuente(op.concepto)
            lineas_pago.append(LineaAsiento(cta, nom, CERO, liq.retefuente, tercero, op.centro_costo, "Retención practicada", documento))
        if liq.reteiva > 0:
            lineas_pago.append(
                LineaAsiento(CUENTAS["reteiva"][0], CUENTAS["reteiva"][1], CERO, liq.reteiva, tercero, op.centro_costo, "ReteIVA practicada", documento)
            )
        if liq.reteica > 0:
            lineas_pago.append(
                LineaAsiento(CUENTAS["reteica"][0], CUENTAS["reteica"][1], CERO, liq.reteica, tercero, op.centro_costo, "ReteICA practicada", documento)
            )
        asientos.append(Asiento("Pago", op.fecha_pago, documento, "Pago de la factura y retenciones", lineas_pago))

        # 3) Pago de retenciones: pasivo contra banco.
        if liq.total_retenciones > 0:
            lineas_retenciones: list[LineaAsiento] = []
            if liq.retefuente > 0:
                cta, nom = cuenta_retefuente(op.concepto)
                lineas_retenciones.append(LineaAsiento(cta, nom, liq.retefuente, CERO, tercero, op.centro_costo, "Pago de retefuente", documento))
            if liq.reteiva > 0:
                lineas_retenciones.append(
                    LineaAsiento(CUENTAS["reteiva"][0], CUENTAS["reteiva"][1], liq.reteiva, CERO, tercero, op.centro_costo, "Pago de reteIVA", documento)
                )
            if liq.reteica > 0:
                lineas_retenciones.append(
                    LineaAsiento(CUENTAS["reteica"][0], CUENTAS["reteica"][1], liq.reteica, CERO, tercero, op.centro_costo, "Pago de reteICA", documento)
                )
            lineas_retenciones.append(
                LineaAsiento(
                    CUENTAS["bancos"][0],
                    CUENTAS["bancos"][1],
                    CERO,
                    liq.total_retenciones,
                    tercero,
                    op.centro_costo,
                    "Pago de retenciones",
                    documento,
                )
            )
            asientos.append(
                Asiento("Pago de retenciones", op.fecha_pago, documento, "Pago de las retenciones practicadas", lineas_retenciones)
            )

        return asientos

    # ------------------------------------------------------------------
    # Certificados
    # ------------------------------------------------------------------
    def _crear_certificados(self, liq: Liquidacion) -> list[CertificadoRetencion]:
        op = liq.operacion
        certificados: list[CertificadoRetencion] = []

        def base_cert(tipo: str, concepto: str, base: Decimal, tarifa: Decimal, valor: Decimal, fundamento: str) -> CertificadoRetencion:
            return CertificadoRetencion(
                tipo=tipo,
                numero=f"{tipo[:3].upper()}-{op.numero}-{liq.uvt_anio}",
                anio_gravable=liq.uvt_anio,
                agente_nit=liq.comprador.nit,
                agente_nombre=liq.comprador.razon_social,
                retenido_nit=liq.proveedor.nit,
                retenido_nombre=liq.proveedor.razon_social,
                concepto=concepto,
                base=base,
                tarifa=tarifa,
                valor=valor,
                fundamento=fundamento,
                ciudad=liq.comprador.municipio,
                fecha_expedicion=op.fecha_pago,
            )

        if liq.retefuente > 0 and liq.regla_rf:
            certificados.append(
                base_cert(
                    "Renta",
                    liq.regla_rf.concepto.value,
                    liq.base_rf,
                    liq.tarifa_rf,
                    liq.retefuente,
                    liq.regla_rf.fundamento,
                )
            )
        if liq.reteiva > 0:
            certificado = base_cert(
                "ReteIVA",
                f"ReteIVA sobre {op.concepto.value}",
                liq.base_reteiva,
                liq.tarifa_reteiva,
                liq.reteiva,
                "Art. 437-2 ET; Decreto 1625 de 2016, art. 1.6.1.12.13.",
            )
            certificado.base_sin_iva = liq.base_pago
            certificado.iva = liq.iva_pago
            certificados.append(certificado)
        if liq.reteica > 0 and liq.regla_ica:
            certificados.append(
                base_cert(
                    "ReteICA",
                    f"ReteICA — {liq.regla_ica.actividad}",
                    liq.base_reteica,
                    liq.tarifa_reteica,
                    liq.reteica,
                    liq.regla_ica.fundamento,
                )
            )
        for certificado in certificados:
            faltantes = certificado.validar()
            if faltantes:
                raise CalculoBloqueado(
                    f"El certificado {certificado.numero} está incompleto: {', '.join(faltantes)}."
                )
        return certificados

    # ------------------------------------------------------------------
    # Checklist documental
    # ------------------------------------------------------------------
    def _crear_checklist(self, liq: Liquidacion) -> list[ItemChecklist]:
        op = liq.operacion
        items = [
            ItemChecklist("RUT del proveedor", True, liq.proveedor.rut_recibido, "Falta el RUT." if not liq.proveedor.rut_recibido else ""),
            ItemChecklist("Factura electrónica validada", True, op.factura_validada, "" if op.factura_validada else "No validada por la DIAN."),
            ItemChecklist("Orden de compra", True, op.orden_compra, "" if op.orden_compra else "Falta la orden de compra."),
            ItemChecklist("Acta de recibido", True, op.acta_recibido, "" if op.acta_recibido else "Falta el acta de recibido."),
            ItemChecklist("Cálculo de retención", True, True, "Generado por el motor."),
            ItemChecklist("Asiento contable", True, liq.asientos_cuadran, "" if liq.asientos_cuadran else "El asiento no cuadra."),
        ]
        if liq.retefuente > 0:
            items.append(ItemChecklist("Certificado de renta", True, True, "Art. 381 ET."))
        if liq.reteiva > 0:
            items.append(ItemChecklist("Certificado de reteIVA", True, True, "Base sin IVA, IVA, tarifa y valor."))
        if liq.reteica > 0:
            items.append(ItemChecklist("Certificado de reteICA", True, True, "Requisitos municipales."))
        if liq.retefuente > 0 or liq.reteiva > 0:
            items.append(ItemChecklist("Borrador Formulario 350", True, True, "No se presenta automáticamente."))
        if liq.reteica > 0:
            items.append(ItemChecklist("Borrador declaración municipal", True, True, "No se presenta automáticamente."))
        return items

    # ------------------------------------------------------------------
    # Auditoría
    # ------------------------------------------------------------------
    def _crear_auditoria(self, liq: Liquidacion) -> RegistroAuditoria:
        entrada = {
            "comprador": asdict(liq.comprador),
            "proveedor": asdict(liq.proveedor),
            "operacion": asdict(liq.operacion),
            "uvt": liq.uvt,
            "version_tabla": VERSION_TABLAS,
        }
        entrada_json = json.dumps(entrada, default=str, ensure_ascii=False, sort_keys=True)
        resultado_json = json.dumps(liq.resumen(), default=str, ensure_ascii=False, sort_keys=True)
        regla_id = liq.regla_rf.id if liq.regla_rf else ""
        fundamento = liq.regla_rf.fundamento if liq.regla_rf else ""
        documentos = tuple(cert.numero for cert in liq.certificados) + tuple(
            item.documento for item in liq.checklist if item.obligatorio and item.recibido
        )
        return RegistroAuditoria(
            usuario=self.usuario,
            fecha_hora=datetime.now(),
            version_tabla=VERSION_TABLAS,
            uvt=liq.uvt,
            uvt_anio=liq.uvt_anio,
            regla_id=regla_id,
            fundamento=fundamento,
            hash_entrada=hashlib.sha256(entrada_json.encode("utf-8")).hexdigest(),
            entrada_json=entrada_json,
            resultado_json=resultado_json,
            documentos=documentos,
            cambios=("Creación de la liquidación",),
        )


def borradores_declaracion(liq: Liquidacion) -> Any:
    """Resumen para los borradores de Formulario 350 y declaración municipal."""
    filas = []
    if liq.retefuente > 0:
        filas.append(
            {
                "Declaración": "Formulario 350",
                "Concepto": "Retefuente",
                "Base": cop(liq.base_rf),
                "Tarifa": porcentaje(liq.tarifa_rf),
                "Valor": cop(liq.retefuente),
            }
        )
    if liq.reteiva > 0:
        filas.append(
            {
                "Declaración": "Formulario 350",
                "Concepto": "ReteIVA",
                "Base": cop(liq.iva_pago),
                "Tarifa": porcentaje(liq.tarifa_reteiva),
                "Valor": cop(liq.reteiva),
            }
        )
    if liq.reteica > 0 and liq.regla_ica:
        filas.append(
            {
                "Declaración": f"Municipal — {liq.regla_ica.municipio}",
                "Concepto": "ReteICA",
                "Base": cop(liq.base_reteica),
                "Tarifa": porcentaje(liq.tarifa_reteica),
                "Valor": cop(liq.reteica),
            }
        )
    return filas


def explicar(liq: Liquidacion) -> str:
    op = liq.operacion
    lineas = [
        f"Concepto: {op.concepto.value}",
        f"Base factura: {cop(liq.datos.base)}",
        f"IVA: {cop(liq.datos.iva)} ({porcentaje(liq.datos.tarifa_iva)})",
        f"Total factura: {cop(liq.datos.total)}",
    ]
    if liq.factor_pago < 1:
        lineas.append(
            f"Pago parcial: {porcentaje(liq.factor_pago)} de la factura; "
            f"base del pago {cop(liq.base_pago)}, IVA del pago {cop(liq.iva_pago)}."
        )
    if liq.regla_rf:
        lineas.extend(
            [
                f"Mínimo retefuente: {liq.minimo_rf_uvt} UVT = {cop(liq.minimo_rf_valor)} → "
                f"{'cumple' if liq.cumple_minimo_rf else 'no cumple'}",
                f"Tarifa retefuente: {porcentaje(liq.tarifa_rf)} "
                f"({'declarante' if liq.proveedor.declarante else 'no declarante'})",
                f"Retefuente: {cop(liq.retefuente)}",
                f"Fundamento: {liq.regla_rf.fundamento}",
            ]
        )
    else:
        lineas.append("Retefuente: no aplica (comprador no agente, SIMPLE o autorretenedor).")

    if liq.aplica_reteiva:
        lineas.append(
            f"ReteIVA: {cop(liq.reteiva)} = {porcentaje(liq.tarifa_reteiva)} del IVA "
            f"({cop(liq.iva_pago)})."
        )
    else:
        lineas.append("ReteIVA: no aplica.")

    if liq.aplica_reteica and liq.regla_ica:
        lineas.append(
            f"ReteICA: {cop(liq.reteica)} = {porcentaje(liq.tarifa_reteica)} "
            f"({liq.regla_ica.municipio}, {liq.regla_ica.actividad})."
        )
    else:
        lineas.append("ReteICA: no aplica.")

    lineas.extend(
        [
            f"Total retenciones: {cop(liq.total_retenciones)}",
            f"Neto a pagar: {cop(liq.neto)}",
            f"Escenario de la tabla: {liq.fila_decision.numero if liq.fila_decision else 'no tabulado'}",
        ]
    )
    return "\n".join(lineas)


@dataclass(frozen=True)
class CasoPrueba:
    numero: int
    nombre: str
    comprador: Comprador
    proveedor: Proveedor
    operacion: Operacion
    esperado: dict[str, Decimal]


def comprador_sas(
    *,
    agente_reteiva: bool = False,
    agente_reteica: bool = False,
    gran_contribuyente: bool = False,
    municipio: str = "Bogotá",
) -> Comprador:
    return Comprador(
        nit="900.123.456-1",
        razon_social="Comprador SAS",
        tipo=TipoPersona.JURIDICA,
        agente_retefuente=True,
        agente_reteiva=agente_reteiva,
        agente_reteica=agente_reteica,
        municipio=municipio,
        responsable_iva=True,
        obligado_contabilidad=True,
        regimen=Regimen.ORDINARIO,
        direccion="Calle 1 # 2-3",
        gran_contribuyente=gran_contribuyente,
    )


def comprador_gran(*, agente_reteica: bool = False) -> Comprador:
    return comprador_sas(agente_reteiva=True, agente_reteica=agente_reteica, gran_contribuyente=True)


def proveedor_declarante(**cambios: Any) -> Proveedor:
    base = dict(
        nit="800.987.654-2",
        razon_social="Proveedor Declarante SAS",
        tipo=TipoPersona.JURIDICA,
        residente=True,
        declarante=True,
        responsable_iva=True,
        simple=False,
        autorretenedor=False,
        autorretencion_especial=False,
        gran_contribuyente=False,
        actividad_ciiu="6201",
        municipio="Bogotá",
        rut_recibido=True,
        soporte_no_declarante=True,
        actividad_gravada_ica=True,
    )
    base.update(cambios)
    return Proveedor(**base)


def proveedor_no_declarante(**cambios: Any) -> Proveedor:
    base = dict(
        nit="1.012.345.678",
        razon_social="Proveedor Persona Natural",
        tipo=TipoPersona.NATURAL,
        residente=True,
        declarante=False,
        responsable_iva=True,
        simple=False,
        autorretenedor=False,
        autorretencion_especial=False,
        gran_contribuyente=False,
        actividad_ciiu="7410",
        municipio="Bogotá",
        rut_recibido=True,
        soporte_no_declarante=True,
        actividad_gravada_ica=True,
    )
    base.update(cambios)
    return Proveedor(**base)


def proveedor_simple(**cambios: Any) -> Proveedor:
    base = dict(
        nit="901.555.000-4",
        razon_social="Proveedor SIMPLE SAS",
        tipo=TipoPersona.JURIDICA,
        residente=True,
        declarante=False,
        responsable_iva=True,
        simple=True,
        autorretenedor=False,
        autorretencion_especial=False,
        gran_contribuyente=False,
        actividad_ciiu="6202",
        municipio="Bogotá",
        rut_recibido=True,
        soporte_no_declarante=True,
        actividad_gravada_ica=True,
    )
    base.update(cambios)
    return Proveedor(**base)


def proveedor_autorretenedor(**cambios: Any) -> Proveedor:
    base = dict(
        nit="900.777.111-5",
        razon_social="Proveedor Autorretenedor SAS",
        tipo=TipoPersona.JURIDICA,
        residente=True,
        declarante=True,
        responsable_iva=True,
        simple=False,
        autorretenedor=True,
        autorretencion_especial=False,
        gran_contribuyente=False,
        actividad_ciiu="6203",
        municipio="Bogotá",
        rut_recibido=True,
        soporte_no_declarante=True,
        actividad_gravada_ica=True,
    )
    base.update(cambios)
    return Proveedor(**base)


def operacion(
    numero: str,
    concepto: Concepto = Concepto.SERVICIO_GENERAL,
    *,
    base: Any | None = None,
    iva: Any | None = None,
    total: Any | None = None,
    tarifa_iva: Any = "0.19",
    total_incluye_iva: bool = False,
    iva_excluido: bool = False,
    descuentos: Any = "0",
    valor_pagado: Any | None = None,
    fecha_emision: date = date(2026, 10, 15),
    fecha_pago: date = date(2026, 10, 15),
    **cambios: Any,
) -> Operacion:
    datos = dict(
        tipo_documento=TipoDocumento.FACTURA,
        numero=numero,
        fecha_emision=fecha_emision,
        fecha_pago=fecha_pago,
        concepto=concepto,
        descripcion=f"Operación de prueba {numero}",
        base=D(base) if base is not None else None,
        tarifa_iva=D(tarifa_iva),
        iva=D(iva) if iva is not None else None,
        total=D(total) if total is not None else None,
        total_incluye_iva=total_incluye_iva,
        descuentos=D(descuentos),
        moneda="COP",
        trm=None,
        forma_pago="Contado",
        valor_pagado=D(valor_pagado) if valor_pagado is not None else None,
        retencion_ya_practicada=False,
        factura_validada=True,
        orden_compra=True,
        acta_recibido=True,
        periodo_cerrado=False,
        iva_excluido=iva_excluido,
        centro_costo="ADMIN",
    )
    datos.update(cambios)
    return Operacion(**datos)


def casos_diseno() -> list[CasoPrueba]:
    return [
        CasoPrueba(
            1,
            "Servicio declarante",
            comprador_sas(),
            proveedor_declarante(),
            operacion("FV-001", base=2_000_000),
            {"iva_pago": D("380000"), "retefuente": D("80000"), "reteiva": CERO, "reteica": CERO, "neto": D("2300000")},
        ),
        CasoPrueba(
            2,
            "Servicio no declarante",
            comprador_sas(),
            proveedor_no_declarante(),
            operacion("FV-002", base=500_000),
            {"iva_pago": D("95000"), "retefuente": D("30000"), "reteiva": CERO, "reteica": CERO, "neto": D("565000")},
        ),
        CasoPrueba(
            3,
            "Bajo mínimo",
            comprador_sas(),
            proveedor_no_declarante(),
            operacion("FV-003", base=90_000),
            {"iva_pago": D("17100"), "retefuente": CERO, "reteiva": CERO, "reteica": CERO, "neto": D("107100")},
        ),
        CasoPrueba(
            4,
            "Exactamente 2 UVT",
            comprador_gran(),
            proveedor_declarante(),
            operacion("FV-004", base=D("104748")),
            {
                "iva_pago": D("19902.12"),
                "retefuente": D("4189.92"),
                "reteiva": D("2985.32"),
                "reteica": CERO,
                "neto": D("117474.88"),
            },
        ),
        CasoPrueba(
            5,
            "Honorarios jurídicos",
            comprador_sas(),
            proveedor_declarante(),
            operacion("FV-005", Concepto.HONORARIOS, base=3_000_000),
            {"iva_pago": D("570000"), "retefuente": D("330000"), "reteiva": CERO, "reteica": CERO, "neto": D("3240000")},
        ),
        CasoPrueba(
            6,
            "Arrendamiento vivienda",
            comprador_sas(),
            proveedor_declarante(),
            operacion("FV-006", Concepto.ARRENDAMIENTO_VIVIENDA, base=1_200_000, tarifa_iva="0", iva_excluido=True),
            {"iva_pago": CERO, "retefuente": D("42000"), "reteiva": CERO, "reteica": CERO, "neto": D("1158000")},
        ),
        CasoPrueba(
            7,
            "Compra declarante",
            comprador_sas(),
            proveedor_declarante(),
            operacion("FV-007", Concepto.COMPRA_BIENES, base=4_000_000),
            {"iva_pago": D("760000"), "retefuente": D("100000"), "reteiva": CERO, "reteica": CERO, "neto": D("4660000")},
        ),
        CasoPrueba(
            8,
            "SIMPLE",
            comprador_gran(),
            proveedor_simple(),
            operacion("FV-008", base=1_000_000),
            {"iva_pago": D("190000"), "retefuente": CERO, "reteiva": D("28500"), "reteica": CERO, "neto": D("1161500")},
        ),
        CasoPrueba(
            9,
            "Autorretenedor",
            comprador_gran(),
            proveedor_autorretenedor(),
            operacion("FV-009", base=1_000_000),
            {"iva_pago": D("190000"), "retefuente": CERO, "reteiva": D("28500"), "reteica": CERO, "neto": D("1161500")},
        ),
        CasoPrueba(
            10,
            "Total con IVA",
            comprador_sas(),
            proveedor_declarante(),
            operacion("FV-010", total=1_190_000, total_incluye_iva=True),
            {"base_pago": D("1000000"), "iva_pago": D("190000"), "retefuente": D("40000"), "reteiva": CERO, "reteica": CERO, "neto": D("1150000")},
        ),
        CasoPrueba(
            11,
            "Pago parcial",
            comprador_gran(),
            proveedor_declarante(),
            operacion("FV-011", base=1_000_000, valor_pagado=595_000),
            {
                "base_pago": D("500000"),
                "iva_pago": D("95000"),
                "total_pago": D("595000"),
                "retefuente": D("20000"),
                "reteiva": D("14250"),
                "reteica": CERO,
                "neto": D("560750"),
            },
        ),
        CasoPrueba(
            12,
            "ReteICA Bogotá",
            comprador_sas(agente_reteica=True),
            proveedor_declarante(),
            operacion("FV-012", base=2_000_000),
            {"iva_pago": D("380000"), "retefuente": D("80000"), "reteiva": CERO, "reteica": D("19320"), "neto": D("2280680")},
        ),
    ]


# ============================================================================
# Interfaz de línea de comandos y persistencia para uso real
# ============================================================================
# Todo lo que sigue usa el motor definido arriba (mismo código del notebook).

import argparse
import csv
import logging
import sys
from pathlib import Path

__version__ = "2026.1"

log = logging.getLogger("motor_liquidador")

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_BLOQUEADO = 2


# ---------------------------------------------------------------------------
# Serialización JSON
# ---------------------------------------------------------------------------
def _json_default(objeto: Any) -> str:
    if isinstance(objeto, Decimal):
        return str(objeto)
    if isinstance(objeto, (date, datetime)):
        return objeto.isoformat()
    if isinstance(objeto, Enum):
        return objeto.value
    if isinstance(objeto, (tuple, set)):
        return list(objeto)
    raise TypeError(f"Tipo no serializable: {type(objeto).__name__}")


def liquidacion_a_dict(liquidacion: Liquidacion) -> dict:
    """Convierte la liquidación completa (incluida la auditoría) a un dict JSON."""
    return asdict(liquidacion)


def guardar_json(ruta: str | Path, objeto: Any) -> None:
    """Escribe JSON atómico (archivo temporal + renombrado)."""
    destino = Path(ruta)
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_name(destino.name + ".tmp")
    temporal.write_text(
        json.dumps(objeto, default=_json_default, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporal.replace(destino)


# ---------------------------------------------------------------------------
# Repositorio de duplicados persistido en archivo
# ---------------------------------------------------------------------------
class RepositorioFacturasArchivo:
    """Igual que RepositorioFacturas, pero guarda el registro en un JSON.

    El motor llama ``existe(proveedor_nit, numero)`` y ``registrar(...)``; esta
    clase persiste cada registro con usuario y fecha para auditoría.
    """

    def __init__(self, ruta: str | Path, usuario: str = "") -> None:
        self.ruta = Path(ruta)
        self.usuario = usuario
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        self._registros: list[dict] = []
        self._claves: set[tuple[str, str]] = set()
        if self.ruta.exists():
            datos = json.loads(self.ruta.read_text(encoding="utf-8"))
            for registro in datos.get("facturas", []):
                clave = (
                    normalizar(str(registro.get("proveedor", ""))),
                    normalizar(str(registro.get("numero", ""))),
                )
                self._registros.append(registro)
                self._claves.add(clave)

    def existe(self, proveedor_nit: str, numero: str) -> bool:
        return (normalizar(proveedor_nit), normalizar(numero)) in self._claves

    def registrar(self, proveedor_nit: str, numero: str, detalle: str = "") -> None:
        clave = (normalizar(proveedor_nit), normalizar(numero))
        if clave in self._claves:
            return
        registro = {
            "proveedor": proveedor_nit,
            "numero": numero,
            "usuario": self.usuario,
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "detalle": detalle,
        }
        self._registros.append(registro)
        self._claves.add(clave)
        guardar_json(self.ruta, {"facturas": self._registros})


# ---------------------------------------------------------------------------
# Conversión de JSON de entrada al modelo
# ---------------------------------------------------------------------------
_SIN_DEFECTO = object()

_ALIASES = {
    (TipoDocumento, "factura"): TipoDocumento.FACTURA,
    (TipoDocumento, "factura de venta"): TipoDocumento.FACTURA,
    (TipoDocumento, "nota credito"): TipoDocumento.NOTA_CREDITO,
    (TipoDocumento, "documento soporte"): TipoDocumento.DOCUMENTO_SOPORTE,
    (Concepto, "servicio"): Concepto.SERVICIO_GENERAL,
    (Concepto, "servicios"): Concepto.SERVICIO_GENERAL,
    (Concepto, "honorario"): Concepto.HONORARIOS,
    (Concepto, "compra"): Concepto.COMPRA_BIENES,
    (Concepto, "compras"): Concepto.COMPRA_BIENES,
    (Concepto, "mercancia"): Concepto.COMPRA_BIENES,
}


def _obligatorio(datos: dict, campo: str) -> None:
    if campo not in datos or datos[campo] in (None, ""):
        raise ValueError(f"Falta el campo obligatorio '{campo}'.")


def _decimal(datos: dict, campo: str, defecto: Any = _SIN_DEFECTO) -> Decimal | None:
    if campo not in datos or datos[campo] in (None, ""):
        if defecto is _SIN_DEFECTO:
            raise ValueError(f"Falta el campo numérico obligatorio '{campo}'.")
        return None if defecto is None else D(defecto)
    return D(datos[campo])


def _booleano(datos: dict, campo: str, defecto: bool = False) -> bool:
    if campo not in datos or datos[campo] is None:
        return defecto
    valor = datos[campo]
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, str):
        texto = normalizar(valor)
        if texto in ("si", "sí", "true", "1", "verdadero"):
            return True
        if texto in ("no", "false", "0", "falso"):
            return False
    raise ValueError(f"El campo '{campo}' debe ser booleano (true/false o sí/no).")


def _fecha(datos: dict, campo: str) -> date:
    _obligatorio(datos, campo)
    try:
        return date.fromisoformat(str(datos[campo]))
    except ValueError:
        raise ValueError(f"El campo '{campo}' debe ser una fecha AAAA-MM-DD.") from None


def _enum(enum_clase: type[Enum], valor: Any, campo: str) -> Enum:
    if isinstance(valor, enum_clase):
        return valor
    objetivo = normalizar(str(valor))
    for miembro in enum_clase:
        if normalizar(miembro.value) == objetivo or normalizar(miembro.name) == objetivo:
            return miembro
    if (enum_clase, objetivo) in _ALIASES:
        return _ALIASES[(enum_clase, objetivo)]
    opciones = ", ".join(f"'{miembro.value}'" for miembro in enum_clase)
    raise ValueError(f"El campo '{campo}' debe ser uno de: {opciones}.")


def comprador_desde_dict(datos: dict) -> Comprador:
    _obligatorio(datos, "nit")
    _obligatorio(datos, "razon_social")
    return Comprador(
        nit=str(datos["nit"]).strip(),
        razon_social=str(datos["razon_social"]).strip(),
        tipo=_enum(TipoPersona, datos.get("tipo", "Jurídica"), "comprador.tipo"),
        agente_retefuente=_booleano(datos, "agente_retefuente"),
        agente_reteiva=_booleano(datos, "agente_reteiva"),
        agente_reteica=_booleano(datos, "agente_reteica"),
        municipio=str(datos.get("municipio", "")).strip(),
        responsable_iva=_booleano(datos, "responsable_iva", True),
        obligado_contabilidad=_booleano(datos, "obligado_contabilidad", True),
        regimen=_enum(Regimen, datos.get("regimen", "Ordinario"), "comprador.regimen"),
        direccion=str(datos.get("direccion", "")).strip(),
        gran_contribuyente=_booleano(datos, "gran_contribuyente"),
        entidad_estatal=_booleano(datos, "entidad_estatal"),
        emisor_tarjetas=_booleano(datos, "emisor_tarjetas"),
    )


def proveedor_desde_dict(datos: dict) -> Proveedor:
    _obligatorio(datos, "nit")
    _obligatorio(datos, "razon_social")
    return Proveedor(
        nit=str(datos["nit"]).strip(),
        razon_social=str(datos["razon_social"]).strip(),
        tipo=_enum(TipoPersona, datos.get("tipo", "Jurídica"), "proveedor.tipo"),
        residente=_booleano(datos, "residente", True),
        declarante=_booleano(datos, "declarante", True),
        responsable_iva=_booleano(datos, "responsable_iva", True),
        simple=_booleano(datos, "simple"),
        autorretenedor=_booleano(datos, "autorretenedor"),
        autorretencion_especial=_booleano(datos, "autorretencion_especial"),
        gran_contribuyente=_booleano(datos, "gran_contribuyente"),
        actividad_ciiu=str(datos.get("actividad_ciiu", "")).strip(),
        municipio=str(datos.get("municipio", "")).strip(),
        rut_recibido=_booleano(datos, "rut_recibido", True),
        soporte_no_declarante=_booleano(datos, "soporte_no_declarante", True),
        actividad_gravada_ica=_booleano(datos, "actividad_gravada_ica", True),
    )


def operacion_desde_dict(datos: dict) -> Operacion:
    _obligatorio(datos, "numero")
    _obligatorio(datos, "concepto")
    return Operacion(
        tipo_documento=_enum(TipoDocumento, datos.get("tipo_documento", "Factura electrónica"), "tipo_documento"),
        numero=str(datos["numero"]).strip(),
        fecha_emision=_fecha(datos, "fecha_emision"),
        fecha_pago=_fecha(datos, "fecha_pago"),
        concepto=_enum(Concepto, datos.get("concepto"), "concepto"),
        descripcion=str(datos.get("descripcion", "")).strip(),
        base=_decimal(datos, "base", None),
        tarifa_iva=_decimal(datos, "tarifa_iva", "0.19"),
        iva=_decimal(datos, "iva", None),
        total=_decimal(datos, "total", None),
        total_incluye_iva=_booleano(datos, "total_incluye_iva"),
        descuentos=_decimal(datos, "descuentos", "0"),
        moneda=str(datos.get("moneda", "COP")).upper().strip(),
        trm=_decimal(datos, "trm", None),
        forma_pago=str(datos.get("forma_pago", "Contado")),
        valor_pagado=_decimal(datos, "valor_pagado", None),
        retencion_ya_practicada=_booleano(datos, "retencion_ya_practicada"),
        factura_validada=_booleano(datos, "factura_validada", True),
        orden_compra=_booleano(datos, "orden_compra", True),
        acta_recibido=_booleano(datos, "acta_recibido", True),
        periodo_cerrado=_booleano(datos, "periodo_cerrado"),
        iva_excluido=_booleano(datos, "iva_excluido"),
        centro_costo=str(datos.get("centro_costo", "ADMIN")).strip() or "ADMIN",
    )


def cargar_entrada(ruta: str) -> dict:
    texto = Path(ruta).read_text(encoding="utf-8")
    datos = json.loads(texto)
    if not isinstance(datos, dict):
        raise ValueError("El archivo de entrada debe ser un objeto JSON con 'comprador', 'proveedor' y 'operaciones'.")
    _obligatorio(datos, "comprador")
    _obligatorio(datos, "proveedor")
    return datos


def cargar_tablas(ruta: str) -> tuple[dict[int, Decimal] | None, tuple[ReglaRetefuente, ...] | None, tuple[ReglaICA, ...] | None]:
    """Carga UVT, retefuente e ICA opcionales desde un JSON (ver comando `plantilla-tablas`)."""
    datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    uvt: dict[int, Decimal] | None = None
    retefuente: tuple[ReglaRetefuente, ...] | None = None
    ica: tuple[ReglaICA, ...] | None = None

    if "uvt" in datos:
        uvt = {}
        for anio, valor in datos["uvt"].items():
            uvt[int(anio)] = D(valor)
    if "retefuente" in datos:
        reglas = []
        for regla in datos["retefuente"]:
            _obligatorio(regla, "id")
            _obligatorio(regla, "condicion")
            reglas.append(
                ReglaRetefuente(
                    id=str(regla["id"]),
                    concepto=_enum(Concepto, regla.get("concepto"), "regla.concepto"),
                    condicion=str(regla["condicion"]).strip(),
                    tarifa=_decimal(regla, "tarifa"),
                    minimo_uvt=_decimal(regla, "minimo_uvt", "0"),
                    base=str(regla.get("base", "Valor antes de IVA, menos descuentos y devoluciones")),
                    fundamento=str(regla.get("fundamento", "")),
                    vigencia_desde=date.fromisoformat(str(regla["vigencia_desde"])),
                    vigencia_hasta=date.fromisoformat(str(regla["vigencia_hasta"])),
                    version=str(regla.get("version", VERSION_TABLAS)),
                )
            )
        retefuente = tuple(reglas)
    if "ica" in datos:
        reglas = []
        for regla in datos["ica"]:
            _obligatorio(regla, "municipio")
            _obligatorio(regla, "actividad")
            reglas.append(
                ReglaICA(
                    municipio=str(regla["municipio"]).strip(),
                    actividad=str(regla["actividad"]).strip(),
                    tarifa=_decimal(regla, "tarifa"),
                    minimo_uvt=_decimal(regla, "minimo_uvt", "0"),
                    fundamento=str(regla.get("fundamento", "")),
                    vigencia_desde=date.fromisoformat(str(regla["vigencia_desde"])),
                    vigencia_hasta=date.fromisoformat(str(regla["vigencia_hasta"])),
                    version=str(regla.get("version", VERSION_TABLAS)),
                )
            )
        ica = tuple(reglas)
    return uvt, retefuente, ica


# ---------------------------------------------------------------------------
# Impresión en texto plano
# ---------------------------------------------------------------------------
def imprimir_alertas(liq: Liquidacion) -> None:
    if not liq.alertas:
        return
    print("\nAlertas:")
    for alerta in liq.alertas:
        print(f"  [{alerta.severidad.value}] {alerta.codigo}: {alerta.mensaje}")


def imprimir_asientos(liq: Liquidacion) -> None:
    for asiento in liq.asientos:
        estado = "cuadra" if asiento.cuadra else "NO CUADRA"
        print(f"\n{asiento.tipo} — {asiento.documento} — {asiento.fecha} ({estado})")
        print(f"{'Cuenta':<10} {'Nombre':<34} {'Débito':>16} {'Crédito':>16}   Tercero / Centro de costo")
        for linea in asiento.lineas:
            print(
                f"{linea.cuenta:<10} {linea.nombre[:34]:<34} "
                f"{(cop(linea.debito) if linea.debito else ''):>16} "
                f"{(cop(linea.credito) if linea.credito else ''):>16}   "
                f"{linea.tercero} / {linea.centro_costo}"
            )
        print(
            f"{'':<10} {'Totales':<34} {cop(asiento.total_debito):>16} {cop(asiento.total_credito):>16}"
        )


def imprimir_certificados(liq: Liquidacion) -> None:
    if not liq.certificados:
        print("\nCertificados: ninguno (no hubo retención).")
        return
    print("\nCertificados:")
    for certificado in liq.certificados:
        print(
            f"  {certificado.tipo}: {certificado.numero} | base {cop(certificado.base)} | "
            f"tarifa {porcentaje(certificado.tarifa)} | valor {cop(certificado.valor)} | "
            f"{certificado.ciudad}, {certificado.fecha_expedicion}"
        )


def imprimir_checklist(liq: Liquidacion) -> None:
    print("\nChecklist documental:")
    for item in liq.checklist:
        estado = "OK " if item.recibido else "FALTA"
        obligatorio = "obligatorio" if item.obligatorio else "opcional"
        detalle = f" — {item.observacion}" if item.observacion else ""
        print(f"  [{estado}] {item.documento} ({obligatorio}){detalle}")


# ---------------------------------------------------------------------------
# Guardado de salidas para el caso real
# ---------------------------------------------------------------------------
def guardar_liquidacion(directorio: str | Path, liq: Liquidacion) -> list[str]:
    """Guarda liquidación (JSON), asientos (CSV) y certificados (CSV).

    CSV con separador ';' y números con punto decimal: abre directo en Excel
    (español) y queda listo para importar al ERP o al sistema contable.
    """
    carpeta = Path(directorio)
    carpeta.mkdir(parents=True, exist_ok=True)
    numero_seguro = "".join(c if c.isalnum() or c in "-_" else "_" for c in liq.operacion.numero)
    archivos: list[str] = []

    ruta_json = carpeta / f"liquidacion_{numero_seguro}.json"
    guardar_json(ruta_json, liquidacion_a_dict(liq))
    archivos.append(str(ruta_json))

    ruta_asientos = carpeta / f"asientos_{numero_seguro}.csv"
    with ruta_asientos.open("w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.writer(archivo, delimiter=";")
        escritor.writerow(
            ["tipo", "fecha", "documento", "cuenta", "nombre", "debito", "credito",
             "tercero", "centro_costo", "descripcion"]
        )
        for asiento in liq.asientos:
            for linea in asiento.lineas:
                escritor.writerow(
                    [
                        asiento.tipo,
                        asiento.fecha.isoformat(),
                        asiento.documento,
                        linea.cuenta,
                        linea.nombre,
                        str(linea.debito),
                        str(linea.credito),
                        linea.tercero,
                        linea.centro_costo,
                        linea.descripcion,
                    ]
                )
    archivos.append(str(ruta_asientos))

    if liq.certificados:
        ruta_certificados = carpeta / f"certificados_{numero_seguro}.csv"
        with ruta_certificados.open("w", encoding="utf-8-sig", newline="") as archivo:
            escritor = csv.writer(archivo, delimiter=";")
            escritor.writerow(
                ["tipo", "numero", "anio_gravable", "agente_nit", "agente_nombre",
                 "retenido_nit", "retenido_nombre", "concepto", "base", "tarifa",
                 "valor", "fundamento", "ciudad", "fecha_expedicion", "base_sin_iva", "iva"]
            )
            for certificado in liq.certificados:
                escritor.writerow(
                    [
                        certificado.tipo,
                        certificado.numero,
                        certificado.anio_gravable,
                        certificado.agente_nit,
                        certificado.agente_nombre,
                        certificado.retenido_nit,
                        certificado.retenido_nombre,
                        certificado.concepto,
                        str(certificado.base),
                        str(certificado.tarifa),
                        str(certificado.valor),
                        certificado.fundamento,
                        certificado.ciudad,
                        certificado.fecha_expedicion.isoformat(),
                        str(certificado.base_sin_iva) if certificado.base_sin_iva is not None else "",
                        str(certificado.iva) if certificado.iva is not None else "",
                    ]
                )
        archivos.append(str(ruta_certificados))

    return archivos


# ---------------------------------------------------------------------------
# Plantillas
# ---------------------------------------------------------------------------
PLANTILLA_ENTRADA = {
    "_ayuda": {
        "fechas": "AAAA-MM-DD",
        "montos": "número o texto, sin separador de miles (2500000 o \"2500000\")",
        "operaciones": "puede ser una lista para procesar un lote completo",
        "notas": "base/iva/total: informe la base, o el total + IVA, o el total con total_incluye_iva=true; "
                 "valor_pagado es opcional (pago total). tarifa_iva: 0.19, 0.05 o 0.",
    },
    "comprador": {
        "nit": "900.123.456-1",
        "razon_social": "Comprador SAS",
        "tipo": "Jurídica",
        "agente_retefuente": True,
        "agente_reteiva": False,
        "agente_reteica": False,
        "municipio": "Bogotá",
        "responsable_iva": True,
        "obligado_contabilidad": True,
        "regimen": "Ordinario",
        "direccion": "Calle 1 # 2-3",
        "gran_contribuyente": False,
        "entidad_estatal": False,
        "emisor_tarjetas": False,
    },
    "proveedor": {
        "nit": "800.987.654-2",
        "razon_social": "Proveedor Ejemplo SAS",
        "tipo": "Jurídica",
        "residente": True,
        "declarante": True,
        "responsable_iva": True,
        "simple": False,
        "autorretenedor": False,
        "autorretencion_especial": False,
        "gran_contribuyente": False,
        "actividad_ciiu": "6201",
        "municipio": "Bogotá",
        "rut_recibido": True,
        "soporte_no_declarante": True,
        "actividad_gravada_ica": True,
    },
    "operaciones": [
        {
            "tipo_documento": "Factura electrónica",
            "numero": "FV-2026-1028",
            "fecha_emision": "2026-10-28",
            "fecha_pago": "2026-10-28",
            "concepto": "Servicio general",
            "descripcion": "Servicio de mantenimiento",
            "base": "2500000",
            "tarifa_iva": "0.19",
            "iva": None,
            "total": None,
            "total_incluye_iva": False,
            "descuentos": "0",
            "moneda": "COP",
            "trm": None,
            "forma_pago": "Contado",
            "valor_pagado": None,
            "retencion_ya_practicada": False,
            "factura_validada": True,
            "orden_compra": True,
            "acta_recibido": True,
            "periodo_cerrado": False,
            "iva_excluido": False,
            "centro_costo": "ADMIN",
        }
    ],
}

PLANTILLA_TABLAS = {
    "_ayuda": {
        "uso": "python motor_liquidador.py calcular --entrada factura.json --tablas este_archivo.json",
        "notas": "Las claves uvt, retefuente e ica son opcionales; si no aparecen, se usan las tablas 2026 del motor.",
    },
    "uvt": {"2026": "52374"},
    "retefuente": [
        {
            "id": "RF-SERV-2026",
            "concepto": "Servicio general",
            "condicion": "declarante",
            "tarifa": "0.04",
            "minimo_uvt": "2",
            "fundamento": "Art. 392 ET; Decreto 572/2025; UVT 2026.",
            "vigencia_desde": "2026-07-01",
            "vigencia_hasta": "2026-12-31",
            "version": "2026.1",
        }
    ],
    "ica": [
        {
            "municipio": "Bogotá",
            "actividad": "Servicios",
            "tarifa": "0.00966",
            "minimo_uvt": "0",
            "fundamento": "Acuerdo 724 de 2026 (verificar actividad y vigencia).",
            "vigencia_desde": "2026-01-01",
            "vigencia_hasta": "2026-12-31",
            "version": "2026.1",
        }
    ],
}


# ---------------------------------------------------------------------------
# Comando `casos`: verificación con los 12 casos del diseño funcional
# ---------------------------------------------------------------------------
def comparar_caso(caso: CasoPrueba, liquidacion: Liquidacion) -> list[str]:
    errores: list[str] = []
    for campo, esperado in caso.esperado.items():
        obtenido = getattr(liquidacion, campo)
        if dinero(obtenido) != dinero(esperado):
            errores.append(f"{campo}: esperado {cop(esperado)}, obtenido {cop(obtenido)}")
    return errores


def _tabla_casos(filas: list[list[Any]]) -> str:
    encabezados = ["#", "Caso", "Base pago", "IVA", "Retefuente", "ReteIVA", "ReteICA", "Neto", "Esc."]
    anchos = [2, 26, 15, 15, 15, 15, 15, 15, 4]
    lineas = [
        "  ".join(f"{encabezados[i]:<{anchos[i]}}" if i != 0 else encabezados[i] for i in range(len(encabezados)))
    ]
    for fila in filas:
        numero = str(fila[0])
        nombre = str(fila[1])[:anchos[1]]
        valores = [numero] + [nombre] + [cop(v) if isinstance(v, Decimal) else str(v) for v in fila[2:]]
        lineas.append(
            f"{valores[0]:<2}  {valores[1]:<{anchos[1]}}  "
            + "  ".join(f"{valores[j]:>{anchos[j]}}" for j in range(2, len(anchos)))
        )
    return "\n".join(lineas)


def comando_casos(args: argparse.Namespace) -> int:
    errores: list[str] = []
    filas: list[list[Any]] = []
    for caso in casos_diseno():
        try:
            liq = LiquidadorRetenciones(usuario="prueba.casos").calcular(caso.comprador, caso.proveedor, caso.operacion)
        except CalculoBloqueado as error:
            errores.append(f"Caso {caso.numero}: {error.mensaje}")
            filas.append([caso.numero, caso.nombre, "BLOQUEADO", "", "", "", "", "", ""])
            continue
        errores.extend(f"Caso {caso.numero}: {mensaje}" for mensaje in comparar_caso(caso, liq))
        filas.append(
            [
                caso.numero,
                caso.nombre,
                liq.base_pago,
                liq.iva_pago,
                liq.retefuente,
                liq.reteiva,
                liq.reteica,
                liq.neto,
                liq.fila_decision.numero if liq.fila_decision else "—",
            ]
        )
    print(_tabla_casos(filas))
    if errores:
        print("\n❌ Casos con diferencias:")
        for mensaje in errores:
            print(" -", mensaje)
        return EXIT_BLOQUEADO
    print("\n✅ Los 12 casos del diseño funcional coinciden con los valores esperados.")
    return EXIT_OK


# ---------------------------------------------------------------------------
# Comando `tablas`: muestra qué tablas usa el motor
# ---------------------------------------------------------------------------
def comando_tablas(args: argparse.Namespace) -> int:
    uvt, retefuente, ica = cargar_tablas(args.tablas) if args.tablas else (None, None, None)
    origen = f"personalizadas desde {args.tablas}" if args.tablas else "por defecto (incluidas en el motor)"
    uvt_efectiva = uvt if uvt is not None else TABLA_UVT
    retefuente_efectiva = tuple(retefuente if retefuente is not None else TABLA_RETEFUENTE)
    ica_efectiva = tuple(ica if ica is not None else TABLA_ICA)

    print(f"Versión de tablas: {VERSION_TABLAS} — {origen}")
    print("\nUVT por año:")
    for anio in sorted(uvt_efectiva):
        print(f"  {anio}: {cop(uvt_efectiva[anio])}")
    print(
        "\nConstantes: IVA general " + porcentaje(IVA_GENERAL) + " (también "
        + porcentaje(IVA_DIFERENCIAL) + " y 0%) | reteIVA " + porcentaje(TARIFA_RETEIVA)
        + " | mínimo reteIVA " + str(MIN_RETEIVA_SERVICIOS_UVT) + " UVT servicios / "
        + str(MIN_RETEIVA_COMPRAS_UVT) + " UVT compras"
    )
    print("\nRetefuente (renta):")
    print(f"{'ID':<14} {'Concepto':<28} {'Condición':<14} {'Tarifa':>8} {'Mín UVT':>8}  {'Vigencia':<21}  Fundamento")
    for regla in retefuente_efectiva:
        print(
            f"{regla.id:<14} {regla.concepto.value[:28]:<28} {regla.condicion:<14} "
            f"{porcentaje(regla.tarifa):>8} {str(regla.minimo_uvt):>8}  "
            f"{regla.vigencia_desde.isoformat()} → {regla.vigencia_hasta.isoformat():<10}  {regla.fundamento}"
        )
    print("\nReteICA:")
    print(f"{'Municipio':<16} {'Actividad':<12} {'Tarifa':>9} {'Mín UVT':>8}  {'Vigencia':<21}  Fundamento")
    for regla in ica_efectiva:
        print(
            f"{regla.municipio[:16]:<16} {regla.actividad[:12]:<12} "
            f"{porcentaje(regla.tarifa):>9} {str(regla.minimo_uvt):>8}  "
            f"{regla.vigencia_desde.isoformat()} → {regla.vigencia_hasta.isoformat():<10}  {regla.fundamento}"
        )
    print(
        "\nValidación contra la norma: DIAN (tabla de retenciones y UVT del año), "
        "SUIN-Juriscol / Diario Oficial (decretos y resoluciones) y el acuerdo municipal de cada "
        "ciudad para reteICA. El fundamento y la vigencia de cada fila deben coincidir con esas fuentes."
    )
    return EXIT_OK


# ---------------------------------------------------------------------------
# Comandos de la interfaz
# ---------------------------------------------------------------------------
def comando_plantilla(args: argparse.Namespace) -> int:
    ruta = Path(args.salida)
    guardar_json(ruta, PLANTILLA_ENTRADA)
    print(f"Plantilla de entrada escrita en: {ruta}")
    print("Úsela así:")
    print(f"  python motor_liquidador.py calcular --entrada {ruta} --usuario 'contador@empresa.com'")
    return EXIT_OK


def comando_plantilla_tablas(args: argparse.Namespace) -> int:
    ruta = Path(args.salida)
    guardar_json(ruta, PLANTILLA_TABLAS)
    print(f"Plantilla de tablas escrita en: {ruta}")
    print("Úsela así:")
    print(f"  python motor_liquidador.py calcular --entrada factura.json --tablas {ruta}")
    return EXIT_OK


def comando_calcular(args: argparse.Namespace) -> int:
    datos = cargar_entrada(args.entrada)
    try:
        comprador = comprador_desde_dict(datos["comprador"])
        proveedor = proveedor_desde_dict(datos["proveedor"])
        if "operaciones" in datos:
            operaciones = [operacion_desde_dict(op) for op in datos["operaciones"]]
        elif "operacion" in datos:
            operaciones = [operacion_desde_dict(datos["operacion"])]
        else:
            raise ValueError("Indique 'operacion' o la lista 'operaciones' en el archivo de entrada.")
    except KeyError as error:
        raise ValueError(f"Falta el campo obligatorio '{error.args[0]}' en el archivo de entrada.") from error
    if not operaciones:
        raise ValueError("La lista de operaciones está vacía.")

    uvt, retefuente, ica = cargar_tablas(args.tablas) if args.tablas else (None, None, None)
    repositorio = (
        RepositorioFacturasArchivo(args.repositorio, usuario=args.usuario) if args.repositorio else None
    )
    liquidador = LiquidadorRetenciones(
        usuario=args.usuario,
        repositorio=repositorio,
        tabla_uvt=uvt,
        tabla_retefuente=retefuente,
        tabla_ica=ica,
    )

    log.info("Comprador: %s (%s)", comprador.razon_social, comprador.nit)
    log.info("Proveedor: %s (%s)", proveedor.razon_social, proveedor.nit)
    log.info("Operaciones a liquidar: %d", len(operaciones))
    if args.tablas:
        log.info("Tablas personalizadas cargadas desde %s", args.tablas)
    if args.repositorio:
        log.info("Repositorio de duplicados: %s", args.repositorio)

    correctas = 0
    bloqueadas = 0
    for op in operaciones:
        try:
            liq = liquidador.calcular(
                comprador, proveedor, op, autorizar_duplicado=args.autorizar_duplicado
            )
        except CalculoBloqueado as error:
            bloqueadas += 1
            print(f"\n🔒 {op.numero}: {error.mensaje}")
            for alerta in error.alertas:
                print(f"   [{alerta.severidad.value}] {alerta.codigo}: {alerta.mensaje}")
            continue

        correctas += 1
        print("\n" + "=" * 78)
        print(explicar(liq))
        imprimir_alertas(liq)
        imprimir_asientos(liq)
        imprimir_certificados(liq)
        imprimir_checklist(liq)
        print(f"\n¿Autorizado para pagar? {'SÍ' if liq.puede_pagar else 'NO'}")
        print(f"AUDITORÍA: usuario={liq.auditoria.usuario} | fecha={liq.auditoria.fecha_hora:%Y-%m-%d %H:%M:%S} | "
              f"tablas={liq.auditoria.version_tabla} | UVT={cop(liq.auditoria.uvt)} | hash={liq.auditoria.hash_entrada[:16]}…")
        if not args.solo_mostrar:
            archivos = guardar_liquidacion(args.salida, liq)
            print("Archivos generados:")
            for archivo in archivos:
                print(f"  - {archivo}")

    print("\n" + "=" * 78)
    print(f"Resumen: {correctas} liquidación(es) correcta(s), {bloqueadas} bloqueada(s).")
    if bloqueadas:
        log.warning("Hubo operaciones bloqueadas: revise los mensajes anteriores. Código de salida %d.", EXIT_BLOQUEADO)
        return EXIT_BLOQUEADO
    return EXIT_OK


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        sys.stderr.write(f"Error: {message}\n")
        self.print_usage(sys.stderr)
        raise SystemExit(EXIT_ERROR)


def construir_parser() -> argparse.ArgumentParser:
    parser = _Parser(
        prog="motor_liquidador.py",
        description="Motor del liquidador de retenciones Colombia 2026 (retefuente, reteIVA, reteICA).",
        epilog=(
            "Ejemplos:\n"
            "  python motor_liquidador.py plantilla\n"
            "  python motor_liquidador.py calcular --entrada plantilla_factura.json --usuario 'contador@empresa.com'\n"
            "  python motor_liquidador.py calcular --entrada lote.json --repositorio registradas.json --salida salidas\n"
            "  python motor_liquidador.py casos\n"
            "  python motor_liquidador.py tablas\n"
            "\nCódigos de salida: 0 = todo liquidado; 1 = error de entrada o archivos; 2 = operaciones bloqueadas por el motor."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--verboso", action="store_true", help="muestra trazas de depuración")

    subparsers = parser.add_subparsers(dest="comando", required=True)

    p_plantilla = subparsers.add_parser("plantilla", help="escribe un ejemplo de archivo de entrada")
    p_plantilla.add_argument("--salida", default="plantilla_factura.json", help="ruta del archivo a escribir")

    p_tablas = subparsers.add_parser("plantilla-tablas", help="escribe un ejemplo de archivo de tablas (UVT, tarifas)")
    p_tablas.add_argument("--salida", default="tablas_personalizadas.json", help="ruta del archivo a escribir")

    p_casos = subparsers.add_parser("casos", help="verifica los 12 casos del diseño funcional")

    p_tablas_cmd = subparsers.add_parser("tablas", help="muestra las tablas (UVT, retefuente, reteICA) que usa el motor")
    p_tablas_cmd.add_argument("--tablas", default=None, help="JSON opcional para ver las tablas personalizadas cargadas")

    p_calcular = subparsers.add_parser("calcular", help="liquida una o varias operaciones desde un JSON")
    p_calcular.add_argument("--entrada", required=True, help="JSON con comprador, proveedor y operaciones")
    p_calcular.add_argument("--salida", default="salidas", help="directorio para los archivos de salida")
    p_calcular.add_argument("--usuario", default="cli", help="usuario que firma la auditoría (ej. contador@empresa.com)")
    p_calcular.add_argument("--repositorio", default=None, help="archivo JSON que registra facturas ya liquidadas (evita duplicados)")
    p_calcular.add_argument("--tablas", default=None, help="JSON opcional con UVT, retefuente e ICA personalizadas")
    p_calcular.add_argument("--autorizar-duplicado", action="store_true", help="permite recalcular una factura ya registrada")
    p_calcular.add_argument("--solo-mostrar", action="store_true", help="imprime el resultado sin guardar archivos")

    for sub in (p_plantilla, p_tablas, p_casos, p_calcular, p_tablas_cmd):
        sub.add_argument("--verboso", action="store_true", help=argparse.SUPPRESS)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = construir_parser()
    args = parser.parse_args(argv)
    nivel = logging.DEBUG if args.verboso else logging.INFO
    logging.basicConfig(level=nivel, format="%(levelname)s: %(message)s", stream=sys.stderr)

    try:
        if args.comando == "plantilla":
            return comando_plantilla(args)
        if args.comando == "plantilla-tablas":
            return comando_plantilla_tablas(args)
        if args.comando == "casos":
            return comando_casos(args)
        if args.comando == "tablas":
            return comando_tablas(args)
        if args.comando == "calcular":
            return comando_calcular(args)
    except CalculoBloqueado as error:
        log.error("Bloqueado: %s", error.mensaje)
        return EXIT_BLOQUEADO
    except (json.JSONDecodeError, ValueError, KeyError, TypeError, FileNotFoundError, OSError) as error:
        log.error("%s", error)
        return EXIT_ERROR
    except Exception:
        log.exception("Error inesperado.")
        return EXIT_ERROR
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
