#!/usr/bin/env python3
"""Build the 16-case withholding control table for the public project."""

from __future__ import annotations

import csv
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

BASE = Path("/home/rimas/liquidador-retenciones")
BASE.mkdir(parents=True, exist_ok=True)

NAVY = "16324F"
BLUE = "1F4E79"
TEAL = "2A7F8F"
GOLD = "C9A227"
LIGHT = "F3F6F9"
PALE_GOLD = "FFF8E6"
PALE_GREEN = "E9F7F1"
PALE_RED = "FDECEC"
DARK = "1F2933"
MUTED = "5F6F7F"
WHITE = "FFFFFF"

FONT = "Calibri"
MONEY = '#,##0.##'
PCT2 = "0.00%"
PCT3 = "0.000%"

thin = Side(style="thin", color="D9E2EA")
border = Border(left=thin, right=thin, top=thin, bottom=thin)


CASES = [
    dict(n=1, title="Servicio general, proveedor declarante, comprador SAS normal", concept="Servicio general",
         buyer="SAS normal; agente RF; no RIVA/RICA", supplier="Persona jurídica declarante; no gran contribuyente",
         base=2_000_000, iva=380_000, rf_rate=0.04, rf=80_000, riva_rate=0, riva=0, rica_rate=0, rica=0,
         asiento="D 5135 / D 240805 / C 220505; pago C 236525",
         docs="Factura, certificado RF, comprobante, Formulario 350",
         errors="No calcular RF sobre el total; no practicar RIVA sin ser agente",
         note="Caso base de servicio general."),
    dict(n=2, title="Servicio general, proveedor no declarante", concept="Servicio general",
         buyer="SAS normal; agente RF; no RIVA/RICA", supplier="Persona natural no declarante; responsable de IVA",
         base=500_000, iva=95_000, rf_rate=0.06, rf=30_000, riva_rate=0, riva=0, rica_rate=0, rica=0,
         asiento="D 5135 / D 240805 / C 220505; pago C 236525",
         docs="RUT, certificación de no declarante, factura, certificado RF, Formulario 350",
         errors="Aplicar 4% en lugar de 6%; no documentar la condición de no declarante",
         note="La base supera 2 UVT."),
    dict(n=3, title="Servicio por debajo del mínimo", concept="Servicio general",
         buyer="SAS normal", supplier="Persona natural no declarante; responsable de IVA",
         base=90_000, iva=17_100, rf_rate=0, rf=0, riva_rate=0, riva=0, rica_rate=0, rica=0,
         asiento="D 5135 / D 240805 / C 111005 (o proveedores)",
         docs="Factura y comprobante de pago; no hay certificado de retención",
         errors="Retener sobre $90.000; aplicar reteIVA sin verificar el mínimo; fragmentar la operación",
         note="Base inferior a 2 UVT ($104.748): no hay retención."),
    dict(n=4, title="Base exactamente en 2 UVT", concept="Servicio general",
         buyer="Gran contribuyente; agente RF y RIVA", supplier="Persona jurídica declarante; no gran contribuyente",
         base=104_748, iva=19_902.12, rf_rate=0.04, rf=4_189.92, riva_rate=0.15, riva=2_985.32, rica_rate=0, rica=0,
         asiento="D 5135 / D 240805 / C 220505; pago C 236525 / C 236701",
         docs="Factura, certificado RF, certificado reteIVA, comprobante, Formulario 350",
         errors="Redondear de forma inconsistente; no definir política de redondeo",
         note="Valores exactos. Redondeo a peso: RF $4.190; RIVA $2.985; neto $117.475."),
    dict(n=5, title="Honorarios, persona jurídica", concept="Honorarios",
         buyer="Gran contribuyente; agente RF y RIVA", supplier="Persona jurídica declarante; no gran contribuyente",
         base=3_000_000, iva=570_000, rf_rate=0.11, rf=330_000, riva_rate=0.15, riva=85_500, rica_rate=0, rica=0,
         asiento="D 5110 / D 240805 / C 220505; pago C 236515 / C 236701",
         docs="Factura, certificado RF, certificado reteIVA, comprobante, Formulario 350",
         errors="Usar 4% de servicios generales; olvidar reteIVA",
         note="Honorarios tienen tarifa distinta a servicios generales."),
    dict(n=6, title="Honorarios, persona natural no declarante", concept="Honorarios",
         buyer="SAS normal; agente RF; no RIVA", supplier="Persona natural no declarante; responsable de IVA",
         base=800_000, iva=152_000, rf_rate=0.10, rf=80_000, riva_rate=0, riva=0, rica_rate=0, rica=0,
         asiento="D 5110 / D 240805 / C 220505; pago C 236515",
         docs="RUT, certificación de no declarante, factura, certificado RF, Formulario 350",
         errors="Aplicar 11%; practicar reteIVA sin ser agente",
         note="La tarifa de no declarante es 10%."),
    dict(n=7, title="Arrendamiento de vivienda", concept="Arrendamiento inmueble",
         buyer="SAS normal; agente RF", supplier="Persona natural declarante; no gran contribuyente",
         base=1_200_000, iva=0, rf_rate=0.035, rf=42_000, riva_rate=0, riva=0, rica_rate=0, rica=0,
         asiento="D 5120 / C 220505; pago C 236530",
         docs="Contrato, factura o documento equivalente, certificado RF, comprobante",
         errors="Cobrar IVA a vivienda; aplicar reteIVA sin IVA; olvidar el mínimo de 10 UVT",
         note="Arrendamiento de vivienda: IVA excluido, base supera 10 UVT."),
    dict(n=8, title="Compra de mercancía, proveedor declarante", concept="Mercancía",
         buyer="Gran contribuyente; agente RF y RIVA", supplier="Persona jurídica declarante; no gran contribuyente",
         base=4_000_000, iva=760_000, rf_rate=0.025, rf=100_000, riva_rate=0.15, riva=114_000, rica_rate=0, rica=0,
         asiento="D 1435 / D 240805 / C 220505; pago C 236540 / C 236701",
         docs="Factura, certificado RF, certificado reteIVA, comprobante, Formulario 350",
         errors="Calcular RF sobre el total con IVA; olvidar el mínimo de 10 UVT",
         note="Caso base de compra de mercancía."),
    dict(n=9, title="Compra de mercancía, proveedor no declarante", concept="Mercancía",
         buyer="SAS normal; agente RF; no RIVA", supplier="Persona natural no declarante; responsable de IVA",
         base=1_000_000, iva=190_000, rf_rate=0.035, rf=35_000, riva_rate=0, riva=0, rica_rate=0, rica=0,
         asiento="D 1435 / D 240805 / C 220505; pago C 236540",
         docs="RUT, certificación de no declarante, factura, certificado RF, Formulario 350",
         errors="Aplicar 2,5%; no documentar la condición de no declarante",
         note="La tarifa de compras para no declarante es 3,5%."),
    dict(n=10, title="Gran contribuyente, servicio", concept="Servicio general",
         buyer="Gran contribuyente; agente RF y RIVA", supplier="Persona jurídica declarante; no gran contribuyente",
         base=5_000_000, iva=950_000, rf_rate=0.04, rf=200_000, riva_rate=0.15, riva=142_500, rica_rate=0, rica=0,
         asiento="D 5135 / D 240805 / C 220505; pago C 236525 / C 236701",
         docs="Factura, certificado RF, certificado reteIVA, comprobante, Formulario 350",
         errors="Olvidar reteIVA por ser gran contribuyente; calcular sobre el total",
         note="El comprador es gran contribuyente y agente de reteIVA."),
    dict(n=11, title="ReteICA en Bogotá", concept="Servicio general",
         buyer="SAS normal; agente RF y reteICA; no RIVA", supplier="Persona jurídica declarante; no gran contribuyente",
         base=2_000_000, iva=380_000, rf_rate=0.04, rf=80_000, riva_rate=0, riva=0, rica_rate=0.00966, rica=19_320,
         asiento="D 5135 / D 240805 / C 220505; pago C 236525 / C 2368",
         docs="Factura, certificado RF, certificado reteICA, comprobante, Formulario 350",
         errors="Usar una tarifa de ICA de otra ciudad; no verificar la calidad de agente municipal",
         note="Tarifa pedagógica 0,966% de Bogotá; verificar tarifa vigente."),
    dict(n=12, title="Proveedor SIMPLE", concept="Servicio general",
         buyer="Gran contribuyente; agente RF y RIVA", supplier="Contribuyente del SIMPLE; responsable de IVA",
         base=1_000_000, iva=190_000, rf_rate=0, rf=0, riva_rate=0.15, riva=28_500, rica_rate=0, rica=0,
         asiento="D 5135 / D 240805 / C 220505; pago C 236701",
         docs="Factura, certificado reteIVA, comprobante; no certificado de RF",
         errors="Practicar retefuente a un proveedor SIMPLE; olvidar reteIVA",
         note="Art. 911 ET: no hay retefuente; reteICA tampoco."),
    dict(n=13, title="Proveedor autorretenedor", concept="Servicio general",
         buyer="Gran contribuyente; agente RF y RIVA", supplier="Autorretenedor de renta; no gran contribuyente",
         base=1_000_000, iva=190_000, rf_rate=0, rf=0, riva_rate=0.15, riva=28_500, rica_rate=0, rica=0,
         asiento="D 5135 / D 240805 / C 220505; pago C 236701",
         docs="Factura, certificado de autorretención, certificado reteIVA, comprobante",
         errors="Practicar retefuente; no verificar la autorización de autorretención",
         note="El proveedor se autorretiene; el comprador solo practica reteIVA."),
    dict(n=14, title="Factura con IVA incluido", concept="Servicio general",
         buyer="SAS normal; agente RF; no RIVA", supplier="Persona jurídica declarante; no gran contribuyente",
         base=1_000_000, iva=190_000, rf_rate=0.04, rf=40_000, riva_rate=0, riva=0, rica_rate=0, rica=0,
         asiento="D 5135 / D 240805 / C 220505; pago C 236525",
         docs="Factura con IVA incluido, certificado RF, comprobante",
         errors="Calcular la base sobre $1.190.000; no separar el IVA",
         note="Total facturado $1.190.000 con IVA incluido; base = 1.190.000 / 1,19."),
    dict(n=15, title="Pago parcial", concept="Servicio general",
         buyer="Gran contribuyente; agente RF y RIVA", supplier="Persona jurídica declarante; no gran contribuyente",
         base=1_000_000, iva=190_000, rf_rate=0.04, rf=40_000, riva_rate=0.15, riva=28_500, rica_rate=0, rica=0,
         asiento="D 5135 / D 240805 / C 220505; pago 50%: C 236525 / C 236701 / C 111005",
         docs="Factura, certificados de retención del pago, comprobante",
         errors="Retener sobre el total cuando solo se paga el 50%; olvidar el saldo",
         note="Pago 50%: base 500.000; IVA 95.000; RF 20.000; RIVA 14.250; neto 560.750; saldo 595.000."),
    dict(n=16, title="Nota crédito antes del pago", concept="Servicio general",
         buyer="SAS normal; agente RF; no RIVA", supplier="Persona jurídica declarante; no gran contribuyente",
         base=1_000_000, iva=190_000, rf_rate=0.04, rf=40_000, riva_rate=0, riva=0, rica_rate=0, rica=0,
         asiento="D 5135 / D 240805 / C 220505; NC 50%; pago C 236525",
         docs="Factura original, nota crédito, certificado RF sobre el saldo, comprobante",
         errors="Retener sobre la factura original completa; no reversar la retención de la nota crédito",
         note="Factura original 2.000.000 + IVA 380.000; NC 50% por 1.190.000; saldo 1.190.000; RF 40.000."),
]


def title(ws, text: str, subtitle: str = "") -> None:
    ws.merge_cells("A1:U1")
    c = ws["A1"]
    c.value = text
    c.font = Font(name=FONT, size=20, bold=True, color=WHITE)
    c.fill = PatternFill("solid", fgColor=NAVY)
    c.alignment = Alignment(vertical="center", horizontal="left")
    ws.row_dimensions[1].height = 38
    if subtitle:
        ws.merge_cells("A2:U2")
        c = ws["A2"]
        c.value = subtitle
        c.font = Font(name=FONT, size=10.5, italic=True, color=MUTED)
        c.fill = PatternFill("solid", fgColor=LIGHT)
        c.alignment = Alignment(vertical="center", horizontal="left", wrap_text=True)
        ws.row_dimensions[2].height = 28


def section(ws, row: int, text: str, width: int = 5) -> None:
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=width)
    c = ws.cell(row=row, column=1, value=text)
    c.font = Font(name=FONT, size=11, bold=True, color=WHITE)
    c.fill = PatternFill("solid", fgColor=BLUE)
    c.alignment = Alignment(vertical="center", horizontal="left")
    ws.row_dimensions[row].height = 24


def note(ws, row: int, text: str, width: int = 5) -> None:
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=width)
    c = ws.cell(row=row, column=1, value=text)
    c.font = Font(name=FONT, size=9, italic=True, color=MUTED)
    c.alignment = Alignment(vertical="top", horizontal="left", wrap_text=True)
    c.fill = PatternFill("solid", fgColor=LIGHT)
    ws.row_dimensions[row].height = 34


def header_row(ws, row: int, headers: list[str]) -> None:
    for col, value in enumerate(headers, 1):
        c = ws.cell(row=row, column=col, value=value)
        c.font = Font(name=FONT, size=9.3, bold=True, color=WHITE)
        c.fill = PatternFill("solid", fgColor=NAVY)
        c.alignment = Alignment(vertical="center", horizontal="center", wrap_text=True)
        c.border = border
    ws.row_dimensions[row].height = 34


def body_row(ws, row: int, values: list, money_cols: set[int] | None = None,
             pct2_cols: set[int] | None = None, pct3_cols: set[int] | None = None) -> None:
    money_cols = money_cols or set()
    pct2_cols = pct2_cols or set()
    pct3_cols = pct3_cols or set()
    for col, value in enumerate(values, 1):
        c = ws.cell(row=row, column=col, value=value)
        c.font = Font(name=FONT, size=9.4, color=DARK)
        c.alignment = Alignment(vertical="top", horizontal="left", wrap_text=True)
        c.border = border
        if col in money_cols:
            c.number_format = MONEY
            c.alignment = Alignment(vertical="top", horizontal="right")
        if col in pct2_cols:
            c.number_format = PCT2
            c.alignment = Alignment(vertical="top", horizontal="right")
        if col in pct3_cols:
            c.number_format = PCT3
            c.alignment = Alignment(vertical="top", horizontal="right")


def widths(ws, values: list[int]) -> None:
    for i, value in enumerate(values, 1):
        ws.column_dimensions[get_column_letter(i)].width = value


def setup(ws, tab_color: str = NAVY, landscape: bool = True) -> None:
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = tab_color
    ws.page_setup.orientation = "landscape" if landscape else "portrait"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_options.horizontalCentered = True


def build() -> None:
    wb = Workbook()
    wb.properties.title = "Liquidador de retenciones Colombia 2026 — 16 casos de control"
    wb.properties.creator = "Kelvis Samir Copete Córdoba"
    wb.properties.subject = "Tabla de control de retenciones: retefuente, reteIVA y reteICA"
    wb.calculation.fullCalcOnLoad = True

    # Casos
    ws = wb.active
    ws.title = "Casos"
    setup(ws, NAVY)
    widths(ws, [5, 36, 20, 34, 36, 13, 13, 13, 8, 13, 8, 13, 8, 13, 15, 13, 40, 40, 40, 45, 10])
    title(ws, "16 casos de control — retenciones Colombia 2026",
          "Cada fila es un caso independiente. No sumar bases entre casos. UVT 2026: $52.374.")
    headers = ["#", "Caso", "Concepto", "Comprador", "Proveedor", "Base", "IVA", "Total",
               "RF %", "RF", "RIVA %", "RIVA", "RICA %", "RICA", "Total retenciones", "Neto",
               "Asiento", "Documentos", "Errores a evitar", "Nota", "Chequeo"]
    header_row(ws, 4, headers)
    r = 5
    for case in CASES:
        total = case["base"] + case["iva"]
        total_ret = case["rf"] + case["riva"] + case["rica"]
        net = total - total_ret
        values = [case["n"], case["title"], case["concept"], case["buyer"], case["supplier"],
                  case["base"], case["iva"], total, case["rf_rate"], case["rf"],
                  case["riva_rate"], case["riva"], case["rica_rate"], case["rica"],
                  total_ret, net, case["asiento"], case["docs"], case["errors"], case["note"]]
        body_row(ws, r, values, money_cols={6, 7, 8, 10, 12, 14, 15, 16},
                 pct2_cols={9, 11}, pct3_cols={13})
        # check formula: total - retenciones - net = 0
        c = ws.cell(row=r, column=21, value=f"=H{r}-O{r}-P{r}")
        c.font = Font(name=FONT, size=9.5, bold=True, color="1F7A5A")
        c.fill = PatternFill("solid", fgColor=PALE_GREEN)
        c.number_format = MONEY
        c.border = border
        c.alignment = Alignment(horizontal="right")
        r += 1
    ws.auto_filter.ref = f"A4:U{r-1}"
    ws.freeze_panes = "A5"
    ws.sheet_view.zoomScale = 85
    note_row = r + 1
    ws.merge_cells(start_row=note_row, start_column=1, end_row=note_row, end_column=21)
    c = ws.cell(row=note_row, column=1, value="Chequeo = Total − Total retenciones − Neto. Debe ser 0 en todas las filas. Caso 4 usa valores exactos con decimales; los demás están en pesos enteros.")
    c.font = Font(name=FONT, size=9, italic=True, color=MUTED)
    c.fill = PatternFill("solid", fgColor=LIGHT)
    c.alignment = Alignment(vertical="center", horizontal="left", wrap_text=True)
    ws.row_dimensions[note_row].height = 30

    # Resumen
    ws = wb.create_sheet("Resumen")
    setup(ws, GOLD, landscape=False)
    widths(ws, [4, 44, 18, 50])
    title(ws, "Resumen de cobertura", "Indicadores de la tabla de control. Los totales monetarios son referenciales, no una declaración.")
    section(ws, 4, "INDICADORES", 4)
    rows = [
        ("Casos totales", "=COUNTA(Casos!A5:A20)", "16 casos del paquete."),
        ("Casos con retefuente", "=COUNTIF(Casos!J5:J20,\">0\")", "Incluye servicios, honorarios, arrendamiento y compras."),
        ("Casos con reteIVA", "=COUNTIF(Casos!L5:L20,\">0\")", "Solo cuando el comprador es agente de reteIVA."),
        ("Casos con reteICA", "=COUNTIF(Casos!N5:N20,\">0\")", "Caso 11: tarifa pedagógica de Bogotá."),
        ("Casos sin retención", "=COUNTIF(Casos!O5:O20,0)", "Caso 3: base inferior al mínimo."),
        ("Suma de retenciones (referencial)", "=SUM(Casos!O5:O20)", "No sumar para una declaración; cada caso es independiente."),
        ("Chequeo total (debe ser 0)", "=SUM(Casos!U5:U20)", "Si no es 0, revisar fórmulas."),
    ]
    r = 5
    for label, formula, detail in rows:
        ws.cell(row=r, column=2, value=label).font = Font(name=FONT, size=10, bold=True, color=NAVY)
        c = ws.cell(row=r, column=3, value=formula)
        c.font = Font(name=FONT, size=10, bold=True, color=DARK)
        c.border = border
        c.alignment = Alignment(horizontal="right")
        if "Suma" in label or "Chequeo" in label:
            c.number_format = MONEY
        ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=4)
        ws.cell(row=r, column=4, value=detail).font = Font(name=FONT, size=9.5, color=MUTED)
        ws.cell(row=r, column=4).alignment = Alignment(vertical="top", wrap_text=True)
        for col in (2, 3, 4):
            ws.cell(row=r, column=col).border = border
        r += 1

    section(ws, 14, "COBERTURA POR CONCEPTO", 4)
    header_row(ws, 15, ["", "Concepto", "Casos", "Observación"])
    concept_rows = [
        ("Servicio general", '=COUNTIF(Casos!C5:C20,"Servicio general")', "Casos 1, 2, 3, 4, 10, 11, 12, 13, 14, 15 y 16."),
        ("Honorarios", '=COUNTIF(Casos!C5:C20,"Honorarios")', "Casos 5 y 6."),
        ("Arrendamiento inmueble", '=COUNTIF(Casos!C5:C20,"Arrendamiento inmueble")', "Caso 7."),
        ("Mercancía", '=COUNTIF(Casos!C5:C20,"Mercancía")', "Casos 8 y 9."),
    ]
    r = 16
    for concept, formula, obs in concept_rows:
        ws.cell(row=r, column=2, value=concept).font = Font(name=FONT, size=10, color=DARK)
        c = ws.cell(row=r, column=3, value=formula)
        c.font = Font(name=FONT, size=10, bold=True, color=NAVY)
        c.alignment = Alignment(horizontal="center")
        ws.cell(row=r, column=4, value=obs).font = Font(name=FONT, size=9.5, color=MUTED)
        for col in (2, 3, 4):
            ws.cell(row=r, column=col).border = border
        r += 1

    note(ws, 22, "La tabla es un instrumento de control y aprendizaje. No reemplaza la validación del contador ni la consulta de la norma vigente.", 4)

    # Reglas
    ws = wb.create_sheet("Reglas")
    setup(ws, BLUE)
    widths(ws, [4, 44, 18, 50])
    title(ws, "Reglas y mínimos usados", "Base pedagógica del proyecto. Verifica siempre la vigencia y el RUT del proveedor.")
    section(ws, 4, "PARÁMETROS 2026", 4)
    params = [
        ("UVT 2026", "$52.374", "Valor de referencia del ejercicio."),
        ("2 UVT", "$104.748", "Mínimo de servicios."),
        ("10 UVT", "$523.740", "Mínimo de compras y arrendamiento de inmuebles."),
        ("IVA general", "19%", "Operaciones gravadas."),
        ("Retefuente servicios", "4% declarante / 6% no declarante", "Base antes de IVA; mínimo 2 UVT."),
        ("Retefuente honorarios", "11% jurídica declarante / 10% no declarante", "Sin mínimo general; verificar excepción de 3.300 UVT."),
        ("Retefuente compras", "2,5% declarante / 3,5% no declarante", "Base antes de IVA; mínimo 10 UVT."),
        ("Retefuente arrendamiento inmueble", "3,5%", "Mínimo 10 UVT; vivienda con IVA excluido."),
        ("ReteIVA", "15% del IVA", "Solo si el comprador es agente de reteIVA."),
        ("ReteICA", "Tarifa municipal", "Caso 11 usa 0,966% de Bogotá como ejemplo pedagógico."),
    ]
    header_row(ws, 5, ["", "Concepto", "Valor", "Observación"])
    r = 6
    for concept, value, obs in params:
        ws.cell(row=r, column=2, value=concept).font = Font(name=FONT, size=10, bold=True, color=NAVY)
        ws.cell(row=r, column=3, value=value).font = Font(name=FONT, size=10, color=DARK)
        ws.cell(row=r, column=4, value=obs).font = Font(name=FONT, size=9.5, color=MUTED)
        ws.cell(row=r, column=4).alignment = Alignment(vertical="top", wrap_text=True)
        for col in (2, 3, 4):
            ws.cell(row=r, column=col).border = border
        r += 1

    section(ws, 17, "BANDERAS DEL COMPRADOR Y DEL PROVEEDOR", 4)
    flags = [
        ("Comprador agente de retefuente", "Aplica RF", "Si no es agente, no practica retención."),
        ("Comprador agente de reteIVA", "Aplica 15% del IVA", "No todos los agentes de RF son agentes de reteIVA."),
        ("Comprador agente de reteICA", "Aplica tarifa municipal", "Depende del municipio y de la designación."),
        ("Proveedor declarante", "Tarifa general", "Persona jurídica o natural obligada a declarar."),
        ("Proveedor no declarante", "Tarifa incrementada", "Se debe documentar la condición."),
        ("Proveedor SIMPLE", "No RF / no ICA", "Art. 911 ET; revisar excepciones."),
        ("Proveedor autorretenedor", "No RF del comprador", "El proveedor se autorretiene; el comprador puede practicar reteIVA."),
    ]
    header_row(ws, 18, ["", "Bandera", "Efecto", "Regla"])
    r = 19
    for flag, effect, rule in flags:
        ws.cell(row=r, column=2, value=flag).font = Font(name=FONT, size=10, bold=True, color=NAVY)
        ws.cell(row=r, column=3, value=effect).font = Font(name=FONT, size=10, color=DARK)
        ws.cell(row=r, column=4, value=rule).font = Font(name=FONT, size=9.5, color=MUTED)
        ws.cell(row=r, column=4).alignment = Alignment(vertical="top", wrap_text=True)
        for col in (2, 3, 4):
            ws.cell(row=r, column=col).border = border
        r += 1

    note(ws, 28, "Fuentes de referencia: Estatuto Tributario arts. 381, 437-1, 462-1 y 911; Decreto 572 de 2025; Auto 30229 de 2026; tabla municipal de ICA. La tabla oficial y la norma vigente prevalecen.", 4)

    # Checklist
    ws = wb.create_sheet("Checklist")
    setup(ws, TEAL)
    widths(ws, [5, 36, 34, 34, 34, 34, 14])
    title(ws, "Checklist de revisión", "Marca cada caso cuando hayas validado cálculo, asiento, documentos y errores.")
    header_row(ws, 4, ["#", "Caso", "Cálculo", "Asiento", "Documentos", "Errores a evitar", "Estado"])
    r = 5
    for case in CASES:
        values = [case["n"], case["title"], f"Base {case['base']:,.0f} + IVA {case['iva']:,.2f}; RF {case['rf']:,.2f}; RIVA {case['riva']:,.2f}; RICA {case['rica']:,.2f}.",
                  case["asiento"], case["docs"], case["errors"], "Pendiente"]
        body_row(ws, r, values)
        r += 1
    dv = DataValidation(type="list", formula1='"Pendiente,Revisado,Con error"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"G5:G{r-1}")
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:G{r-1}"

    # Fuentes
    ws = wb.create_sheet("Fuentes")
    setup(ws, GOLD, landscape=False)
    widths(ws, [4, 40, 80])
    title(ws, "Fuentes y alcance", "Documentación de referencia del proyecto.")
    section(ws, 4, "FUENTES", 3)
    sources = [
        ("Estatuto Tributario", "Arts. 381 (certificado de retención), 437-1 (IVA), 462-1 (reteIVA), 911 (SIMPLE)."),
        ("Decreto 572 de 2025", "Modificaciones a retenciones; base mínima de servicios de 2 UVT."),
        ("Auto 30229 de 2026", "Decisión del Consejo de Estado sobre la suspensión y vigencia."),
        ("UVT 2026", "$52.374; 2 UVT = $104.748; 10 UVT = $523.740."),
        ("Tabla municipal de ICA", "Tarifas y mínimos por municipio; el caso 11 usa 0,966% de Bogotá como ejemplo."),
    ]
    r = 5
    for source, detail in sources:
        ws.cell(row=r, column=2, value=source).font = Font(name=FONT, size=10, bold=True, color=NAVY)
        ws.cell(row=r, column=3, value=detail).font = Font(name=FONT, size=9.8, color=DARK)
        ws.cell(row=r, column=3).alignment = Alignment(vertical="top", wrap_text=True)
        for col in (2, 3):
            ws.cell(row=r, column=col).border = border
        ws.row_dimensions[r].height = 34
        r += 1

    section(ws, 12, "ALCANCE Y LÍMITES", 3)
    limits = [
        "Casos educativos con datos ficticios.",
        "No incluye renta, nómina, pagos al exterior, AIU especial, prorrata de IVA ni moneda extranjera.",
        "No reemplaza la revisión de un contador ni la consulta de la norma vigente.",
        "Las tarifas y mínimos deben validarse contra el RUT, el concepto, el municipio y la fecha de la operación.",
    ]
    r = 13
    for text in limits:
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
        c = ws.cell(row=r, column=2, value="• " + text)
        c.font = Font(name=FONT, size=10, color=DARK)
        c.alignment = Alignment(vertical="top", wrap_text=True)
        ws.row_dimensions[r].height = 28
        r += 1

    wb.save(BASE / "Control_Retenciones_16_Casos.xlsx")
    print("OK: Control_Retenciones_16_Casos.xlsx")

    # CSV
    with (BASE / "casos.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.writer(fh, delimiter=";")
        writer.writerow(["#", "Caso", "Concepto", "Comprador", "Proveedor", "Base", "IVA", "Total",
                         "RF %", "RF", "RIVA %", "RIVA", "RICA %", "RICA", "Total retenciones", "Neto",
                         "Asiento", "Documentos", "Errores", "Nota"])
        for c in CASES:
            total = c["base"] + c["iva"]
            total_ret = c["rf"] + c["riva"] + c["rica"]
            net = total - total_ret
            writer.writerow([c["n"], c["title"], c["concept"], c["buyer"], c["supplier"],
                             c["base"], c["iva"], total, c["rf_rate"], c["rf"], c["riva_rate"], c["riva"],
                             c["rica_rate"], c["rica"], total_ret, net, c["asiento"], c["docs"],
                             c["errors"], c["note"]])
    print("OK: casos.csv")


if __name__ == "__main__":
    build()
