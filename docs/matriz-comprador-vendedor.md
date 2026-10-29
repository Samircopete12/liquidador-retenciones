# Matriz comprador–vendedor y tipos de retención (Colombia 2026)

**Corte:** 27/10/2026.  
**UVT 2026:** $52.374.  
**Alcance:** operaciones nacionales, proveedores residentes y comprador persona jurídica con contabilidad.  
**Uso:** material de estudio y referencia para el diseño del liquidador. No es asesoría tributaria.

> **Idea central:** “retención en la fuente” no es una sola cosa. El liquidador debe decidir por separado si aplica **retefuente (renta)**, **reteIVA (IVA)** y **reteICA (ICA)**. El tipo de comprador y el tipo de vendedor son dos ejes, pero no los únicos: también importan el concepto, la base, el mínimo, el municipio y la fecha de la operación.

---

## 1. Las tres retenciones que entran al liquidador

| Retención | Impuesto que anticipa | Quién la practica | Base | Tarifa general | Destino |
|---|---|---|---|---|---|
| **Retefuente** | Renta | Agente de retención de renta: personas jurídicas y asimiladas, entidades públicas, personas naturales comerciantes por encima de 30.000 UVT y designados por la DIAN. | Valor antes de IVA, menos descuentos y devoluciones. | 4% / 6% en servicios; 11% / 10% en honorarios; 2,5% / 3,5% en compras; etc. | DIAN. Formulario 350. |
| **ReteIVA** | IVA | Solo el agente de reteIVA del artículo 437-2 del ET: entidades estatales, grandes contribuyentes, emisores de tarjetas, responsables de IVA que compran a SIMPLE o contratan no residentes, y designados por la DIAN. | IVA facturado. | 15% del IVA. 100% en casos especiales. | DIAN. Formulario 350. |
| **ReteICA** | ICA | Agente designado por el municipio. No todo comprador lo es, ni siquiera un gran contribuyente nacional. | Valor antes de IVA, menos descuentos y devoluciones. | Tarifa municipal de la actividad del vendedor (CIIU). Ejemplo pedagógico: Barranquilla 12,5 por mil; Bogotá 9,66 por mil. | Municipio. Declaración municipal. |

### 1.1 Qué condición mirar en cada una

| Retención | Condición del comprador | Condición del vendedor | Condición de la operación |
|---|---|---|---|
| Retefuente | ¿Es agente de retención de renta? | ¿Es declarante o no declarante? ¿Es SIMPLE? ¿Es autorretenedor? ¿Es no residente? | ¿Cuál es el concepto? ¿La base supera el mínimo? ¿La fecha está dentro de la vigencia? |
| ReteIVA | ¿Es agente de reteIVA para **esta** operación? | ¿Es responsable de IVA? ¿Es SIMPLE? ¿Es gran contribuyente? ¿Es no residente? | ¿La operación está gravada? ¿El IVA está facturado? ¿Supera el mínimo? ¿Hay exclusión entre agentes? |
| ReteICA | ¿Está designado como agente en el municipio del vendedor? | ¿La actividad está gravada en ese municipio? ¿Es SIMPLE? | ¿Cuál es la tarifa municipal? ¿Supera el mínimo municipal? |

> **Regla de oro:** una calidad no se infiere de otra. Ser responsable de IVA no convierte al comprador en agente de reteIVA. Ser gran contribuyente no lo convierte automáticamente en agente de reteICA. Ser autorretenedor de renta no elimina la reteIVA.

### 1.2 Otras figuras que conviene nombrar

| Figura | Qué es | Por qué no entra en la v1 |
|---|---|---|
| Autorretención de renta | El propio vendedor se practica la retención; el comprador no la descuenta del pago. | La v1 la trata como bandera de exclusión, no como cálculo. |
| Retención asumida | El comprador asume la retención y no la descuenta del pago. | Requiere un tratamiento contable y legal especial. |
| Retención de nómina | Retención de renta sobre pagos laborales. | Fuera del alcance del liquidador de compras. |
| Retención por pagos al exterior | Retención de renta o IVA a proveedores no residentes. | Requiere análisis de residencia, CDI y tipo de servicio. |

---

## 2. La tabla del video y la matriz depurada

### 2.1 La tabla del video

El video muestra una matriz de **comprador vs. vendedor** con los regímenes de IVA y las calidades especiales. Esta es la transcripción de la tabla que aparece en pantalla:

| Comprador \ Vendedor | No responsable de IVA | Régimen Simple | Responsable de IVA | Gran contribuyente | Autorretenedor |
|---|---|---|---|---|---|
| **No responsable de IVA** | No aplica | No aplica | No aplica | No aplica | No aplica |
| **Régimen Simple** | No aplica | No aplica | No aplica | No aplica | No aplica |
| **Responsable de IVA** | Retefuente + ReteICA | ReteIVA | Retefuente + ReteICA | Retefuente + ReteICA | No aplica |
| **Gran contribuyente** | Retefuente + ReteICA | ReteIVA | Retefuente + ReteICA + ReteIVA | Retefuente + ReteICA | No aplica |
| **Autorretenedor** | Retefuente + ReteICA | ReteIVA | Retefuente + ReteICA + ReteIVA | Retefuente + ReteICA | No aplica |

**Cómo se lee:** las filas son el comprador (quien practica la retención); las columnas son el vendedor (quien la soporta). Cada celda dice qué retenciones aplican. La tabla no muestra tarifas, mínimos, municipio ni fecha.

### 2.2 Qué simplifica la tabla del video

La tabla es una excelente herramienta pedagógica, pero no es una regla legal completa. Para el liquidador hay que tener en cuenta:

1. **“Responsable de IVA” no es sinónimo de “agente de reteIVA”.** La tabla usa el régimen como proxy. En el caso del comprador “Responsable de IVA” no agrega reteIVA; en el caso del “Gran contribuyente” sí. Eso funciona para los ejemplos, pero la prueba legal es la lista cerrada del artículo 437-2, no la etiqueta del régimen.
2. **“Autorretenedor” no es una sola calidad.** La tabla lo trata como una categoría única y dice “No aplica” cuando el vendedor es autorretenedor. En la práctica hay que distinguir la autorretención general de renta (RUT código 15), la autorretención especial (código 59) y las reglas municipales o de IVA. La autorretención de renta no excluye automáticamente la reteIVA ni la reteICA.
3. **El comprador “Autorretenedor” no es automáticamente agente de reteIVA.** La tabla le atribuye reteIVA como si fuera un gran contribuyente. Eso solo es correcto si además es gran contribuyente o está en la lista del artículo 437-2. La autorretención es una calidad frente a su propia renta, no una autorización para retenerle IVA a otros.
4. **El comprador SIMPLE no retiene, pero el vendedor ordinario puede autorretenerse.** El artículo 911 del ET excluye al SIMPLE de practicar retenciones (salvo pagos laborales), pero cuando el SIMPLE compra a un vendedor ordinario que es agente, ese vendedor debe actuar como agente autorretenedor de renta. La nota al pie de la tabla del video lo dice.
5. **El comprador “No responsable de IVA” puede ser agente de retefuente.** La tabla lo manda a “No aplica” en todos los casos. Una persona natural no responsable de IVA que sea comerciante con ingresos superiores a 30.000 UVT puede ser agente de retención de renta. Hay que verificar la calidad de agente por separado.
6. **La exclusión entre grandes contribuyentes es solo para reteIVA.** La tabla acierta al no poner reteIVA entre GC y GC, pero sí mantiene retefuente y reteICA. No extiendas esa exclusión a las otras dos retenciones.

### 2.3 Matriz depurada para el liquidador

La siguiente matriz usa un **servicio general nacional** como ejemplo. Para compras de bienes, la retefuente cambia de tarifa, pero la lógica de “quién retiene a quién” es la misma. La columna RICA se marca como **M** cuando depende de la designación municipal; si el comprador no es agente en ese municipio, vale 0.

**Convenciones:**

- **RF** = retefuente (renta).
- **RIVA** = reteIVA.
- **RICA** = reteICA.
- **M** = tarifa municipal, solo si el comprador es agente de reteICA en el municipio del vendedor.
- **No** = no aplica en ese escenario.
- Las tarifas entre paréntesis son las de un servicio general: 4% para declarante y 6% para no declarante.

| # | Comprador | Vendedor | RF | RIVA | RICA | Explicación |
|---:|---|---|---|---|---|---|
| 1 | SAS normal: agente RF; no agente general de reteIVA; no agente de reteICA en el ejemplo | PJ declarante, responsable de IVA, no gran contribuyente, no autorretenedor | **Sí (4%)** | **No** | **No** | Caso base. El comprador no está en la lista general del artículo 437-2. |
| 1b | SAS normal | Gran contribuyente, responsable de IVA, no autorretenedor | **Sí (4%)** | **No** | **No** | El comprador no es agente de reteIVA; aunque lo fuera, la exclusión entre agentes impediría la retención. |
| 2 | SAS normal | PN no declarante, responsable de IVA | **Sí (6%)** | **No** | **No** | La tarifa de renta sube por la condición de no declarante. |
| 3 | SAS normal | SIMPLE, responsable de IVA | **No** | **Sí (15%)** | **No** | El SIMPLE no soporta retefuente ni reteICA, pero el comprador responsable de IVA sí es agente de reteIVA frente al SIMPLE (art. 437-2, num. 9). |
| 4 | SAS normal | Autorretenedor de renta, responsable de IVA | **No** | **No** | **No** | El vendedor se autorretiene la renta. El comprador no es agente general de reteIVA. |
| 5 | Gran contribuyente: agente RF y reteIVA; agente de reteICA en el ejemplo | PJ declarante, responsable de IVA, no gran contribuyente, no autorretenedor | **Sí (4%)** | **Sí (15%)** | **M** | Caso del video: Éxito compra a un proveedor normal. |
| 6 | Gran contribuyente | PN no declarante, responsable de IVA | **Sí (6%)** | **Sí (15%)** | **M** | La condición de no declarante cambia la retefuente, no la reteIVA. |
| 7 | Gran contribuyente | SIMPLE, responsable de IVA | **No** | **Sí (15%)** | **No** | SIMPLE: sin RF ni ICA; la reteIVA sigue por el numeral 9 del artículo 437-2. |
| 8 | Gran contribuyente | Gran contribuyente, responsable de IVA, no autorretenedor | **Sí (4%)** | **No** | **M** | Exclusión del parágrafo 1 del artículo 437-2: ventas entre agentes de los numerales 1, 2 y 5 no llevan reteIVA. |
| 9 | Gran contribuyente | Autorretenedor de renta, no gran contribuyente, responsable de IVA | **No** | **Sí (15%)** | **M** | El autorretenedor se practica la renta; el comprador sí puede practicar reteIVA. |
| 10 | Entidad estatal: agente RF y reteIVA; agente de reteICA en el ejemplo | PJ declarante, responsable de IVA, no gran contribuyente | **Sí (4%)** | **Sí (15%)** | **M** | La entidad estatal es agente de reteIVA por el numeral 1 del artículo 437-2. |
| 11 | Entidad estatal | Gran contribuyente | **Sí (4%)** | **No** | **M** | Exclusión entre agentes de los numerales 1 y 2 del artículo 437-2. |
| 12 | Persona natural no agente de RF, IVA ni ICA | Cualquier vendedor residente | **No** | **No** | **No** | Sin calidad de agente no hay retención, aunque el vendedor sea declarante. |
| 13 | Comprador agente de RF | Vendedor no responsable de IVA | **Sí (tarifa del concepto)** | **No** | **M, si la actividad está gravada** | Sin IVA facturado no hay reteIVA; la retefuente y la reteICA pueden seguir aplicando. |
| 14 | Comprador agente de RF y reteIVA | Vendedor no residente | **Tarifa especial (20% / 33% / etc.)** | **100% del IVA** | **Verificar** | Fuera del alcance de la v1. El sistema debe bloquear y pedir revisión. |

**Diferencias deliberadas con la tabla del video:**

- La matriz depurada no usa “autorretenedor” como tipo de comprador. Un autorretenedor de renta no es automáticamente agente de reteIVA; para esa retención importa la lista del artículo 437-2.
- En la columna “Autorretenedor” del vendedor, la tabla del video dice “No aplica”. La matriz depurada separa la autorretención de renta de la reteIVA: si el vendedor es autorretenedor de renta pero responsable de IVA, y el comprador es gran contribuyente, la reteIVA puede aplicar. Verifica qué impuestos cubre la autorretención.
- La tabla del video no muestra la reteICA municipal; la matriz depurada la marca **M** porque depende de la designación del municipio.
- La tabla del video no muestra tarifas, mínimos ni vigencias; esos datos se consultan en la tabla de conceptos y en la norma.

### 2.4 Lectura rápida

- **La retefuente depende de la renta del vendedor y del concepto**, no del IVA. Un vendedor no responsable de IVA puede seguir soportando retefuente.
- **La reteIVA depende de la calidad del comprador y del IVA del vendedor**, no de que ambos sean “responsables de IVA”.
- **La reteICA depende del municipio y de la actividad del vendedor**. Es la más variable de las tres.
- **SIMPLE y autorretenedor no son sinónimos.** El SIMPLE está fuera de retefuente y reteICA por regla general; el autorretenedor solo se excluye de la retefuente que practicaría el comprador.

---

## 3. Tarifas de retefuente por concepto

Esta es la tabla que se usa después de la matriz: la matriz dice **si aplica**; esta tabla dice **cuánto**.

> **Comparación con la tabla del video:** la tabla que muestra el video es la tabla oficial resumida. Incluye filas que no están en el alcance de este liquidador (salarios, comisiones bursátiles y financieras, canasta cultural) y redondea los mínimos a miles ($524.000, $105.000, $3.666.000). Este documento usa el valor exacto de la UVT y solo los conceptos del alcance. Si comparas ambas tablas, la diferencia de pesos es redondeo, no una tarifa distinta.

| Concepto | Declarante | No declarante | Mínimo 2026 | Nota |
|---|---:|---:|---:|---|
| Servicios en general | 4% | 6% | 2 UVT ($104.748) | La base es el valor antes de IVA. |
| Honorarios y comisiones | 11% | 10% | Sin mínimo | 11% para personas jurídicas y declarantes; 10% para no declarantes. Excepción de 3.300 UVT. |
| Arrendamiento de bienes inmuebles | 3,5% | 3,5% | 10 UVT ($523.740) | Aplica a vivienda y, con matices, a otros inmuebles. |
| Arrendamiento de bienes muebles | 4% | 4% | Sin mínimo | No confundir con inmuebles. |
| Compras generales | 2,5% | 3,5% | 10 UVT ($523.740) | Bienes corporales muebles. |
| Transporte de carga | 1% | 1% | 2 UVT ($104.748) | Terrestre, aéreo o marítimo. |
| Transporte de pasajeros terrestre | 3,5% | 3,5% | 10 UVT ($523.740) | Verifica el tipo de transporte. |
| Transporte de pasajeros aéreo/marítimo | 1% | 1% | 2 UVT ($104.748) | Verifica el tipo de transporte. |
| Hoteles y restaurantes | 3,5% | 3,5% | 2 UVT ($104.748) | Puede haber INC; no lo confundas con IVA. |
| Aseo y vigilancia | 2% | 2% | 2 UVT ($104.748) | Caso especial de AIU; revisa doctrina vigente. |
| Servicios temporales | 1% | 1% | 2 UVT ($104.748) | Caso especial de AIU; revisa doctrina vigente. |
| Salud IPS | 2% | 2% | 2 UVT ($104.748) | Servicios integrales de salud. |
| Emolumentos eclesiásticos | 4% | 3,5% | 10 UVT ($523.740) | Verifica la condición del beneficiario. |
| Contratos de construcción | 2% | 2% | 10 UVT ($523.740) | Obra material de bien inmueble. |

### 3.1 Conceptos especiales que conviene bloquear en la v1

| Concepto | Tarifa | Mínimo | Advertencia |
|---|---:|---:|---|
| Licenciamiento o derecho de uso de software | 3,5% declarante; no declarante: verificar | Verificar | La tabla oficial distingue software y consultoría informática. |
| Análisis, diseño, desarrollo, implementación y mantenimiento de software | 3,5% declarante; no declarante: verificar | Verificar | No confundir con servicios generales. |
| Consultoría y administración delegada | 11% jurídica / 10% no declarante | Sin mínimo | Verificar el contrato y el concepto. |
| Consultoría en ingeniería de infraestructura | 6% declarante / 10% no declarante | Sin mínimo | Proyectos de infraestructura y edificaciones. |
| Servicios de sísmica | 6% declarante / 10% no declarante | Sin mínimo | Sector hidrocarburos. |
| Servicios de publicidad | 4% / 6% (verificar) | 2 UVT | Tratamiento según el contrato y el medio. |
| Servicios de seguros | 4% / 6% (verificar) | 2 UVT | Verificar el concepto. |
| Compras con tarjeta débito/crédito | 1,5% | Sin mínimo | Establecimientos afiliados. |
| Combustibles derivados del petróleo | 0,1% | Sin mínimo | Distribuidores mayoristas o minoristas. |
| Compras de bienes agrícolas sin procesamiento | 1,5% | 70 UVT ($3.666.180) | Opción de no retener por debajo del mínimo. |
| Café pergamino o cereza | 0,5% | 70 UVT ($3.666.180) | No confundir con café trillado. |
| Loterías, rifas y apuestas | 20% | 48 UVT ($2.513.952) | Juegos y azar. |
| Rendimientos financieros | 7% | Sin mínimo | No es un servicio. |
| Pagos al exterior (servicios) | 20% | Sin mínimo | Requiere análisis de residencia, CDI y tipo de servicio. |
| Pagos al exterior (administración/dirección) | 33% | Sin mínimo | Artículo 124 del ET. |
| Pagos al exterior (intereses de crédito a un año o más) | 15% | Sin mínimo | Verificar plazo y condiciones. |

> La tabla completa, con la línea de tiempo de la base mínima de servicios y las advertencias de vigencia, está en [`tabla-retenciones-2026.md`](tabla-retenciones-2026.md). Si un concepto no está en la tabla y no tienes la norma a la mano, **no inventes la tarifa**: bloquea el cálculo.

---

## 4. Los dos casos del video, con la matriz aplicada

### 4.1 Compra de La Casa de Papel SAS

- Compra: 60 televisores × $1.055.000 = **$63.300.000**.
- IVA 19%: **$12.027.000**.
- Total factura: **$75.327.000**.
- Comprador: SAS normal, responsable de IVA, agente de retefuente y de reteICA en Barranquilla; **no** es agente general de reteIVA.
- Vendedor: persona jurídica declarante, responsable de IVA, no gran contribuyente.
- En la tabla del video: fila “Responsable de IVA” × columna “Responsable de IVA”. En la matriz depurada: fila 1, con RICA municipal.

| Concepto | Base | Tarifa | Valor |
|---|---:|---:|---:|
| Retefuente | $63.300.000 | 2,5% | $1.582.500 |
| ReteIVA | — | — | $0 |
| ReteICA (Barranquilla, ejemplo) | $63.300.000 | 12,5 por mil | $791.250 |
| **Total retenciones** | | | **$2.373.750** |
| **Neto a pagar** | | | **$72.953.250** |

**Por qué no hay reteIVA:** el comprador es responsable de IVA, pero no está en la lista de agentes de reteIVA del artículo 437-2. La sola responsabilidad de IVA no lo faculta para retener.

### 4.2 Venta a Almacenes Éxito

- Venta: 45 televisores × $2.000.000 = **$90.000.000**.
- IVA 19%: **$17.100.000**.
- Total factura: **$107.100.000**.
- Comprador: Almacenes Éxito, gran contribuyente y autorretenedor; agente de retefuente y reteIVA; reteICA en Barranquilla en el ejemplo.
- Vendedor: persona jurídica declarante, responsable de IVA, no gran contribuyente.
- En la tabla del video: fila “Gran contribuyente” × columna “Responsable de IVA”. En la matriz depurada: fila 5.

| Concepto | Base | Tarifa | Valor |
|---|---:|---:|---:|
| Retefuente | $90.000.000 | 2,5% | $2.250.000 |
| ReteIVA | $17.100.000 | 15% | $2.565.000 |
| ReteICA (Barranquilla, ejemplo) | $90.000.000 | 12,5 por mil | $1.125.000 |
| **Total retenciones** | | | **$5.940.000** |
| **Neto a pagar** | | | **$101.160.000** |

**Por qué hay reteIVA:** el comprador es **gran contribuyente**, y por eso es agente de reteIVA del artículo 437-2. No es porque sea “autorretenedor”: la autorretención es una calidad frente a su propia renta, no una autorización para retenerle IVA a sus proveedores. Si Éxito fuera el vendedor y el comprador también fuera gran contribuyente, la reteIVA no aplicaría por la exclusión del parágrafo 1.

---

## 5. Errores que esta matriz evita

1. **Creer que “responsable de IVA” = “agente de reteIVA”.** No es así. La lista es cerrada y está en el artículo 437-2.
2. **Practicar reteIVA entre dos grandes contribuyentes.** El parágrafo 1 del artículo 437-2 excluye las operaciones entre agentes de los numerales 1, 2 y 5.
3. **Aplicar las tres retenciones solo porque el comprador es “gran contribuyente autorretenedor”.** Hay que revisar al vendedor, la operación y las exclusiones.
4. **Retener retefuente a un proveedor SIMPLE.** El artículo 911 del ET lo excluye, salvo pagos laborales.
5. **Retener retefuente a un autorretenedor.** El vendedor se autorretiene; el comprador no.
6. **No practicar reteIVA al comprar a un SIMPLE.** Si el comprador es responsable de IVA, es agente por el numeral 9 del artículo 437-2.
7. **Practicar reteICA sin ser agente municipal.** La calidad de agente la otorga el municipio, no el tamaño del comprador.
8. **Usar la actividad económica del comprador para la reteICA.** La tarifa es la del vendedor (CIIU).
9. **Incluir el IVA en la base de retefuente o reteICA.** La base es el valor antes de IVA; la base de reteIVA es el IVA.
10. **Ignorar el mínimo, la UVT o la fecha de vigencia.** La regla incluye cuantía y tiempo.

---

## 6. Implicaciones para el diseño del liquidador

### 6.1 Banderas del comprador

- `agente_retefuente`
- `agente_reteiva_general` (entidad estatal, gran contribuyente, emisor de tarjetas, designado)
- `agente_reteiva_simple` (responsable de IVA que compra a SIMPLE)
- `agente_reteiva_no_residente` (responsable de IVA que contrata servicios gravados con no residentes)
- `agente_reteica`
- `gran_contribuyente`
- `entidad_estatal`
- `emisor_tarjetas`
- `responsable_iva`
- `simple`

### 6.2 Banderas del vendedor

- `declarante_renta`
- `responsable_iva`
- `simple`
- `autorretenedor_renta`
- `gran_contribuyente`
- `residencia` (residente / no residente)
- `actividad_ciiu`
- `municipio`

### 6.3 Orden de evaluación

1. **Alcance:** ¿es una operación nacional, con proveedor residente y concepto conocido? Si no, bloquear.
2. **Retefuente:** ¿el comprador es agente? ¿el vendedor es SIMPLE o autorretenedor? ¿la base supera el mínimo? ¿cuál es la tarifa del concepto?
3. **ReteIVA:** ¿la operación está gravada? ¿el vendedor es responsable de IVA? ¿el comprador es agente para este caso? ¿hay exclusión entre agentes? ¿la base supera el mínimo? ¿15% o 100%?
4. **ReteICA:** ¿el comprador es agente en el municipio? ¿la actividad del vendedor está gravada? ¿el vendedor es SIMPLE? ¿cuál es la tarifa y el mínimo municipal?
5. **Neto y redondeo:** total − RF − RIVA − RICA. Redondear con una política única y registrar la diferencia.

### 6.4 Salida esperada por cada retención

Cada retención debe devolver, como mínimo:

- `aplica` (sí/no).
- `base`.
- `tarifa`.
- `valor`.
- `fundamento` (norma, artículo, decreto).
- `vigencia` (desde/hasta).
- `alerta` (por qué no aplica o por qué requiere revisión).

Si falta un dato crítico, el sistema debe **bloquear**, no asumir. En particular: RUT, condición de declarante, responsabilidad de IVA, calidad de agente, municipio, actividad CIIU y fecha de la operación.

---

## 7. Checklist de 60 segundos

- [ ] ¿Separé las tres retenciones?
- [ ] ¿Verifiqué si el comprador es agente de cada una?
- [ ] ¿Verifiqué si el vendedor es declarante, no declarante, SIMPLE o autorretenedor?
- [ ] ¿La operación está gravada con IVA?
- [ ] ¿Hay exclusión de reteIVA entre agentes?
- [ ] ¿La base excluye el IVA?
- [ ] ¿La base supera el mínimo?
- [ ] ¿La tarifa es la del concepto y la del municipio?
- [ ] ¿La fecha está dentro de la vigencia?
- [ ] ¿El neto y el asiento cuadran?

---

## 8. Fuentes y vigencia

- Estatuto Tributario: artículos 368, 392, 401, 437-1, 437-2, 911.
- Decreto 1625 de 2016 (DUR Tributario): artículos 1.2.4.3.1, 1.2.4.9.1, 1.3.2.1.6 y 1.3.2.1.12.
- Decreto 572 de 2025 y Auto 30229 de 2026, para la base mínima de servicios.
- Resolución DIAN 238 de 2025, UVT 2026: $52.374.
- Acuerdos municipales de ICA; en los ejemplos se usa la tarifa pedagógica de Barranquilla (12,5 por mil) y de Bogotá (9,66 por mil).
- Video de referencia: “Retención en la fuente: casos prácticos y contabilización paso a paso”, El Profe Andrés Márquez.

> **Advertencia final:** las tarifas y bases cambian por año, por decreto y por municipio. Antes de usar una regla en producción, verifica la UVT, la fecha de la operación, el RUT del proveedor, la resolución de agentes de reteIVA y el acuerdo municipal de ICA. Si no puedes explicar la regla con su fundamento, no la automatices.
