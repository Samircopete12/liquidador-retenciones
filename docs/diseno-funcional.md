# 09. Diseño funcional del liquidador (sin programar)

**Para qué sirve este módulo:** traducir todo lo aprendido a un diseño que un contador pueda validar y un programador pueda implementar después. Aquí no hay Python ni Excel: hay reglas, datos, decisiones, validaciones y pruebas.

**Idea central:** el liquidador es una **tabla de decisión con memoria**. Debe saber qué regla aplica, con qué base, con qué tarifa, desde cuándo, con qué documento y con qué asiento. Si no puede explicar una regla, no debe automatizarla.

---

## 1. Alcance de la primera versión

### 1.1 Incluye

- Compras nacionales de bienes y servicios.
- Proveedores residentes en Colombia.
- Comprador persona jurídica con contabilidad.
- IVA general 19% y operaciones excluidas/exentas.
- Retefuente de renta.
- ReteIVA como módulo opcional, según la calidad del comprador.
- ReteICA como módulo opcional, según el municipio.
- Proveedores declarantes, no declarantes, SIMPLE y autorretenedores (como banderas).
- Facturas electrónicas y notas crédito simples.
- Asientos de causación, pago y pago de retenciones.
- Certificados y checklist documental.

### 1.2 No incluye (por ahora)

- Pagos al exterior y convenios de doble tributación.
- Régimen simple a fondo (solo la bandera de exclusión).
- Autorretención especial.
- Hidrocarburos, construcción, entidades públicas, sector salud especial.
- Servicios temporales, aseo y vigilancia con AIU (solo advertencia).
- Operaciones entre grandes contribuyentes con reglas especiales.
- Prorrata de IVA.
- Moneda extranjera con diferencia en cambio.
- Declaraciones automáticas ante la DIAN.
- Planeación tributaria o decisiones de negocio.

**Regla de alcance:** si un caso no está en la lista “incluye”, el sistema debe **bloquear** el cálculo y pedir revisión humana. Es mejor no calcular que calcular mal.

---

## 2. Roles y responsabilidades

| Rol | Qué hace |
|---|---|
| Usuario de compras | Registra la operación y adjunta la factura. |
| Contador | Revisa la clasificación, la retención y el asiento. |
| Revisor fiscal / tributarista | Valida reglas, casos especiales y cambios normativos. |
| Administrador de tablas | Actualiza UVT, tarifas, mínimos y vigencias. |
| Auditor | Consulta la trazabilidad y los documentos. |

El sistema no reemplaza al contador. Lo ayuda a ser consistente y deja evidencia.

---

## 3. Entradas del sistema

### 3.1 Datos del comprador

| Campo | Tipo | Obligatorio | Uso |
|---|---|---|---|
| NIT | Texto | Sí | Identificación. |
| Razón social | Texto | Sí | Certificados y asientos. |
| Tipo (jurídica/natural) | Lista | Sí | Determina si es agente de renta. |
| ¿Agente de retefuente? | Sí/No | Sí | Aplica RF. |
| ¿Agente de reteIVA? | Sí/No | Sí | Aplica reteIVA. |
| ¿Agente de reteICA? | Sí/No | Sí | Aplica reteICA. |
| Municipio | Lista | Sí | Tarifa y declaración de ICA. |
| ¿Responsable de IVA? | Sí/No | Sí | IVA descontable. |
| ¿Obligado a llevar contabilidad? | Sí/No | Sí | Devengo vs. causación. |
| Régimen | Lista | Sí | Ordinario, SIMPLE, especial. |
| Dirección y ciudad | Texto | Sí | Certificado. |

### 3.2 Datos del proveedor

| Campo | Tipo | Obligatorio | Uso |
|---|---|---|---|
| NIT | Texto | Sí | Identificación y duplicados. |
| Razón social | Texto | Sí | Certificado. |
| Tipo (jurídica/natural) | Lista | Sí | Tarifa. |
| ¿Residente? | Sí/No | Sí | Nacional/extranjero. |
| ¿Declarante de renta? | Sí/No | Sí | 4% vs. 6%; 2,5% vs. 3,5%; 11% vs. 10%. |
| ¿Responsable de IVA? | Sí/No | Sí | IVA y reteIVA. |
| ¿SIMPLE? | Sí/No | Sí | Exclusión de RF/ICA. |
| ¿Autorretenedor? | Sí/No | Sí | Exclusión de RF. |
| ¿Gran contribuyente? | Sí/No | Sí | ReteIVA. |
| Actividad CIIU | Texto | Sí | Tarifa de ICA. |
| Municipio | Lista | Sí | ICA. |
| RUT / soportes | Archivo | Sí | Evidencia. |

### 3.3 Datos de la operación

| Campo | Tipo | Obligatorio | Uso |
|---|---|---|---|
| Tipo de documento | Lista | Sí | Factura, nota crédito, documento soporte. |
| Número | Texto | Sí | Duplicados y trazabilidad. |
| Fecha de emisión | Fecha | Sí | Vigencia de la regla. |
| Fecha de pago/abono | Fecha | Sí | Momento de la retención. |
| Concepto | Lista | Sí | Tarifa y mínimo. |
| Descripción | Texto | Sí | Clasificación y auditoría. |
| Base | Moneda | Sí | Cálculo. |
| Tarifa de IVA | Lista | Sí | 19%, 5%, 0%, excluido. |
| IVA | Moneda | Calculado | Validación. |
| Total | Moneda | Calculado | Validación. |
| ¿Total incluye IVA? | Sí/No | Sí | Extraer base. |
| Descuentos | Moneda | No | Base neta. |
| Moneda | Lista | Sí | COP/USD. |
| TRM | Número | Si USD | Conversión. |
| Forma de pago | Lista | Sí | Contado/crédito. |
| Valor pagado | Moneda | Sí | Pagos parciales. |
| ¿Retención ya practicada? | Sí/No | Sí | Evitar duplicados. |

### 3.4 Datos de reglas

| Campo | Uso |
|---|---|
| UVT del año | Mínimos y topes. |
| Tabla de conceptos | Tarifa de RF, mínimo, base. |
| Tabla de tarifas de IVA | 19%, 5%, 0%, excluido. |
| Tabla de reteIVA | 15%, 100%, agentes, mínimos. |
| Tabla de reteICA | Municipio, actividad, tarifa, mínimo. |
| Vigencia desde/hasta | Evitar aplicar reglas derogadas. |
| Fundamento legal | Artículo, decreto, resolución. |
| Versión | Auditoría. |

---

## 4. Salidas del sistema

### 4.1 Liquidación

| Campo | Ejemplo |
|---|---|
| Base | $2.000.000 |
| IVA | $380.000 |
| Total | $2.380.000 |
| Concepto de RF | Servicios generales |
| Tarifa RF | 4% |
| Base RF | $2.000.000 |
| RF | $80.000 |
| ¿Aplica reteIVA? | No |
| ReteIVA | $0 |
| ¿Aplica reteICA? | No |
| ReteICA | $0 |
| Neto | $2.300.000 |

### 4.2 Asientos

- Asiento de causación.
- Asiento de pago.
- Asiento de pago de retenciones.
- Asiento de nota crédito, si aplica.

Cada línea debe tener: cuenta, nombre, débito, crédito, tercero, centro de costo, descripción y documento.

### 4.3 Documentos

- Factura validada.
- Certificado de retención por renta, si RF > 0.
- Certificado de reteIVA, si reteIVA > 0.
- Certificado de reteICA, si reteICA > 0.
- Checklist de documentos faltantes.
- Borrador de Formulario 350 (sin presentarlo).
- Borrador de declaración municipal (sin presentarla).

### 4.4 Alertas

- “El comprador no es agente de reteIVA; no se practicó reteIVA.”
- “La base es inferior a 2 UVT; no se practicó retefuente.”
- “El proveedor es SIMPLE; no se practicó retefuente ni reteICA.”
- “El proveedor es autorretenedor; no se practicó retefuente.”
- “Falta el RUT del proveedor.”
- “La factura no está validada.”
- “La tarifa no coincide con la tabla vigente.”
- “El periodo está cerrado.”
- “Posible factura duplicada.”
- “El asiento no cuadra.”

### 4.5 Trazabilidad

- Usuario.
- Fecha y hora.
- Versión de la tabla.
- UVT.
- Regla aplicada.
- Fundamento legal.
- Datos de entrada.
- Resultado.
- Documentos generados.
- Cambios posteriores.

---

## 5. Tabla de decisión

Esta tabla es el corazón del diseño. Cada fila es un escenario; el sistema debe encontrar la fila que corresponda.

| # | Comprador | Proveedor | Concepto | ¿Aplica RF? | ¿Aplica reteIVA? | ¿Aplica reteICA? |
|---|---|---|---|---|---|---|
| 1 | Agente RF, no reteIVA, no reteICA | Declarante | Servicio general | 4% | No | No |
| 2 | Agente RF, no reteIVA, no reteICA | No declarante | Servicio general | 6% | No | No |
| 3 | Agente RF, no reteIVA, no reteICA | Declarante | Honorarios | 11% | No | No |
| 4 | Agente RF, no reteIVA, no reteICA | No declarante | Honorarios | 10% | No | No |
| 5 | Agente RF, no reteIVA, no reteICA | Declarante | Arrendamiento vivienda | 3,5% | No | No |
| 6 | Agente RF, no reteIVA, no reteICA | Declarante | Compra de bienes | 2,5% | No | No |
| 7 | Agente RF, no reteIVA, no reteICA | No declarante | Compra de bienes | 3,5% | No | No |
| 8 | Agente RF y reteIVA | Declarante | Servicio general | 4% | 15% | No |
| 9 | Agente RF y reteIVA | Declarante | Compra de bienes | 2,5% | 15% | No |
| 10 | Agente RF y reteICA | Declarante | Servicio general | 4% | No | Tarifa municipal |
| 11 | Agente RF, reteIVA y reteICA | Declarante | Servicio general | 4% | 15% | Tarifa municipal |
| 12 | Agente RF | SIMPLE | Servicio general | 0% | 15% si es responsable de IVA | 0% |
| 13 | Agente RF | Autorretenedor | Servicio general | 0% | 15% si aplica | Según municipio |
| 14 | No agente RF | Cualquiera | Cualquiera | 0% | Según agente | Según agente |

**Nota:** la tabla es pedagógica. En producción, cada fila debe tener vigencia, fundamento legal y casos de prueba.

---

## 6. Reglas de negocio

### R1. Separar las tres calidades

El sistema debe preguntar por separado si el comprador es agente de retefuente, reteIVA y reteICA. No debe inferir una de otra.

### R2. Base de retefuente

La base de retefuente es el valor antes de IVA, menos descuentos y devoluciones. Nunca incluir el IVA.

### R3. Tarifa de retefuente

La tarifa se toma de la tabla de conceptos, según el concepto y la condición del proveedor (declarante/no declarante, jurídica/natural). Si no hay regla, bloquear.

### R4. Mínimo de retefuente

Antes de calcular, comparar la base con el mínimo del concepto. Si es inferior, no hay retención. Si es igual o superior, sí.

### R5. SIMPLE

Si el proveedor es SIMPLE, retefuente = 0 y reteICA = 0. ReteIVA solo si es responsable de IVA y el comprador es agente.

### R6. Autorretenedor

Si el proveedor es autorretenedor general (RUT código 15), retefuente = 0. ReteIVA y reteICA pueden aplicar. Si solo tiene autorretención especial (código 59), no asumas que está eximido de la retención general: valida el caso.

### R7. No residente

Si el proveedor no es residente, el sistema debe derivar a un módulo de pagos al exterior. No calcular con las tarifas nacionales.

### R8. IVA

IVA = base × tarifa. Si el total incluye IVA, base = total / (1 + tarifa). Validar que la factura discrimine base e IVA.

### R9. ReteIVA

ReteIVA = IVA × 15%, solo si:
- El comprador es agente de reteIVA.
- El proveedor es responsable de IVA.
- La operación está gravada.
- La base supera el mínimo (2 UVT servicios, 10 UVT compras).
- No hay exclusión legal.

### R10. ReteIVA especial

Si el proveedor es no residente y el servicio es gravado, la reteIVA es 100% y no tiene mínimo. Fuera de la v1.

### R11. ReteICA

ReteICA = base × tarifa municipal, solo si:
- El comprador es agente en ese municipio.
- La actividad del vendedor está gravada.
- La base supera el mínimo municipal.
- El proveedor no es SIMPLE.

### R12. Neto

Neto = total − retefuente − reteIVA − reteICA. Validar que el neto no sea negativo.

### R13. Asientos

El asiento debe cuadrar. Si hay diferencia de redondeo, aplicar la política definida y registrarla.

### R14. Certificados

- Si retefuente > 0: certificado de renta.
- Si reteIVA > 0: certificado de IVA.
- Si reteICA > 0: certificado de ICA.
- Si no hay retención: no emitir certificado de ese concepto.

### R15. Documentos

Antes de pagar, el sistema debe verificar:
- RUT del proveedor.
- Factura validada.
- Orden de compra.
- Acta de recibido.
- Cálculo de retención.
- Asiento.

### R16. Vigencia

Cada regla debe tener fecha desde/hasta. Si la operación está fuera de vigencia, bloquear o usar la regla correcta.

### R17. Validaciones de datos

- NIT no vacío.
- Base > 0.
- Tarifa de IVA permitida.
- Total = base + IVA, salvo que el total incluya IVA.
- Fechas coherentes.
- Moneda y TRM.
- Proveedor identificado.

### R18. Duplicados

No permitir dos cálculos para la misma factura (proveedor + número) sin autorización.

### R19. Periodo cerrado

No permitir cambios en periodos cerrados sin un ajuste autorizado.

### R20. Auditoría

Guardar quién, cuándo, qué regla, qué UVT, qué datos y qué resultado.

---

## 7. Validaciones y mensajes

| Validación | Mensaje | Acción |
|---|---|---|
| Falta NIT del proveedor | “El proveedor no está identificado.” | Bloquear pago. |
| Factura no validada | “La factura no está validada por la DIAN.” | Bloquear IVA/costo. |
| Proveedor no declarante sin soporte | “No hay certificación de no declarante.” | Usar tarifa conservadora o bloquear. |
| Base < mínimo | “La base no supera el mínimo; no hay retención.” | Calcular sin retención. |
| Comprador no agente reteIVA | “El comprador no es agente de reteIVA.” | No practicar reteIVA. |
| Proveedor SIMPLE | “Proveedor SIMPLE: no retefuente/reteICA.” | Calcular solo reteIVA si aplica. |
| Proveedor autorretenedor | “Proveedor autorretenedor: no retefuente.” | No practicar RF. |
| Tarifa no encontrada | “No hay regla para este concepto.” | Bloquear y pedir revisión. |
| Asiento no cuadra | “Débitos ≠ créditos.” | No permitir guardar. |
| Posible duplicado | “Ya existe una factura con este número.” | Revisar. |
| Periodo cerrado | “El periodo está cerrado.” | Ajuste autorizado. |

---

## 8. Modelo de datos (conceptual)

### 8.1 Entidades

| Entidad | Campos principales |
|---|---|
| Comprador | NIT, razón social, tipo, agentes, municipio, régimen, responsable IVA. |
| Proveedor | NIT, razón social, tipo, residencia, declarante, responsable IVA, SIMPLE, autorretenedor, CIIU, municipio. |
| Factura | Número, fecha, proveedor, comprador, concepto, base, IVA, total, moneda, estado. |
| Operación | Factura, fecha de pago, valor pagado, forma de pago, retención ya practicada. |
| Regla | Concepto, tarifa, mínimo, vigencia, fundamento, versión. |
| Retención | Tipo, base, tarifa, valor, certificado, declaración. |
| Asiento | Fecha, documento, descripción, líneas. |
| Línea de asiento | Cuenta, nombre, débito, crédito, tercero, centro de costo. |
| Documento | Tipo, archivo, estado, fecha, usuario. |
| Auditoría | Usuario, fecha, acción, regla, resultado. |

### 8.2 Relaciones

- Un comprador tiene muchas facturas.
- Un proveedor tiene muchas facturas.
- Una factura tiene una o varias retenciones.
- Una factura tiene uno o varios asientos.
- Una retención tiene uno o varios certificados.
- Cada cálculo tiene una versión de regla.

---

## 9. Flujo de usuario

### Paso 1: identificar al proveedor

- Buscar por NIT.
- Si no existe, crear con RUT y documentos.
- Mostrar régimen, agentes y alertas.

### Paso 2: registrar la operación

- Número y fecha de factura.
- Concepto.
- Base, IVA, total.
- Forma de pago.
- Valor pagado.

### Paso 3: calcular

- El sistema muestra la regla aplicada.
- Explica base, tarifa, mínimo y resultado.
- Muestra las alertas.

### Paso 4: revisar

- Comparar con la factura.
- Verificar asiento.
- Verificar documentos.
- Aprobar o corregir.

### Paso 5: generar

- Asientos.
- Certificados.
- Checklist.
- Borradores de declaración.
- Archivo.

### Pantalla de “explicación”

Debe mostrar:

```
Concepto: Servicios generales
Base: $2.000.000
Mínimo: 2 UVT = $104.748 → cumple
Tarifa: 4% (proveedor declarante)
Retefuente: $80.000
Fundamento: Art. 392 ET; Decreto 572/2025; UVT 2026.
```

Esto es lo que permite que un contador confíe en el sistema.

---

## 10. Casos de prueba

| # | Caso | Entrada | Resultado esperado |
|---|---|---|---|
| 1 | Servicio declarante | Base $2.000.000, IVA 19%, RF 4% | IVA $380.000; RF $80.000; neto $2.300.000 |
| 2 | Servicio no declarante | Base $500.000, IVA 19%, RF 6% | IVA $95.000; RF $30.000; neto $565.000 |
| 3 | Bajo mínimo | Base $90.000, IVA 19% | RF $0; neto $107.100 |
| 4 | Exactamente 2 UVT | Base $104.748, IVA 19%, RF 4% | RF $4.189,92; reteIVA $2.985,32 si agente |
| 5 | Honorarios jurídicos | Base $3.000.000, IVA 19%, RF 11% | RF $330.000; neto $3.240.000 sin reteIVA |
| 6 | Arrendamiento vivienda | Base $1.200.000, sin IVA, RF 3,5% | RF $42.000; neto $1.158.000 |
| 7 | Compra declarante | Base $4.000.000, IVA 19%, RF 2,5% | RF $100.000; neto $4.660.000 sin reteIVA |
| 8 | SIMPLE | Base $1.000.000, IVA 19%, sin RF | RF $0; reteIVA $28.500 si agente |
| 9 | Autorretenedor | Base $1.000.000, IVA 19%, sin RF | RF $0; reteIVA $28.500 si agente |
| 10 | Total con IVA | Total $1.190.000, IVA 19%, RF 4% | Base $1.000.000; RF $40.000; neto $1.150.000 |
| 11 | Pago parcial | Factura $1.190.000, pago 50%, RF 4%, reteIVA 15% | RF $20.000; reteIVA $14.250; neto $560.750 |
| 12 | ReteICA | Base $2.000.000, 0,966%, RF 4% | ReteICA $19.320; neto $2.280.680 |

**Cada caso debe probar también:**

- Que el asiento cuadre.
- Que el certificado tenga todos los campos.
- Que la alerta correcta aparezca.
- Que el registro de auditoría se genere.

---

## 11. Criterios de aceptación

1. Dado un servicio de $2.000.000 + IVA 19% de un proveedor declarante y un comprador SAS normal, el sistema calcula IVA $380.000, retefuente $80.000 y neto $2.300.000.
2. Dado el mismo caso con un comprador gran contribuyente, el sistema calcula reteIVA $57.000 y neto $2.243.000.
3. Dado un servicio de $90.000, el sistema no practica retefuente ni reteIVA.
4. Dado un proveedor SIMPLE, el sistema no practica retefuente ni reteICA.
5. Dado un proveedor autorretenedor, el sistema no practica retefuente.
6. El asiento de causación y el de pago siempre cuadran.
7. El certificado de renta incluye los siete requisitos del Art. 381.
8. El certificado de IVA incluye base sin IVA, IVA, tarifa y valor.
9. El sistema guarda la versión de la tabla y la UVT usada.
10. El sistema bloquea el cálculo si falta una regla o un dato crítico.

---

## 12. Lo que no se debe automatizar todavía

- La clasificación de servicios ambiguos (¿honorario o servicio general?).
- La determinación de residencia fiscal.
- Los pagos al exterior y convenios.
- Las tarifas municipales de ICA sin fuente actualizada.
- La prorrata de IVA.
- Las operaciones entre grandes contribuyentes.
- Las notas crédito complejas o con efectos fiscales especiales.
- La retención asumida.
- La planeación tributaria.
- La firma de declaraciones.

Estos casos deben ir a **revisión humana obligatoria**. El sistema puede advertir, pero no decidir solo.

---

## 13. Hoja de ruta

### Fase 0: validación manual

- Resolver 20 facturas reales a mano.
- Comparar con la tabla oficial.
- Documentar excepciones.
- Firmar el alcance con un contador.

### Fase 1: diseño

- Tabla de decisión.
- Modelo de datos.
- Casos de prueba.
- Manual de usuario.
- Criterios de aceptación.

### Fase 2: desarrollo

- Implementar las reglas.
- Implementar los asientos.
- Implementar los certificados.
- Implementar la auditoría.

### Fase 3: marcha blanca

- Correr en paralelo con el proceso manual durante un mes.
- Comparar resultados.
- Corregir diferencias.
- Validar con el revisor fiscal.

### Fase 4: producción

- Capacitar usuarios.
- Definir responsables de tablas.
- Monitorear errores.
- Actualizar reglas cuando cambie la UVT o la norma.

---

## 14. Plantilla de regla

Cada regla debe documentarse así:

| Campo | Ejemplo |
|---|---|
| ID | RF-SERV-001 |
| Nombre | Retención por servicios generales |
| Condición | Proveedor declarante, servicio general, base ≥ 2 UVT |
| Tarifa | 4% |
| Base | Valor antes de IVA |
| Mínimo | 2 UVT |
| Fundamento | Art. 392 ET; Decreto 572/2025 |
| Vigencia | Desde 01/07/2026 |
| Excepciones | SIMPLE, autorretenedor, no residente |
| Caso de prueba | Caso 1 |
| Responsable | Contador tributario |

---

## 15. Manual de usuario (esquema)

1. ¿Qué es el liquidador?
2. ¿Qué datos necesito?
3. ¿Cómo registro un proveedor?
4. ¿Cómo registro una factura?
5. ¿Cómo interpreto el cálculo?
6. ¿Cómo reviso el asiento?
7. ¿Cómo genero el certificado?
8. ¿Qué hago si el sistema bloquea?
9. ¿Cómo corrijo un error?
10. ¿Dónde archivo los documentos?
11. ¿Cómo actualizo la UVT y las tarifas?
12. ¿A quién contacto?

---

## 16. Ideas clave

- El liquidador es una tabla de decisión, no una fórmula aislada.
- El alcance debe ser explícito; lo que no está incluido se bloquea.
- Las tres retenciones se deciden por separado.
- La base, el mínimo y la vigencia son tan importantes como la tarifa.
- El asiento y el certificado son parte del producto.
- La trazabilidad es obligatoria.
- La validación con un contador es el paso más importante antes de programar.

Si puedes explicar la tabla de decisión y los 12 casos de prueba, estás listo para la etapa de programación.
