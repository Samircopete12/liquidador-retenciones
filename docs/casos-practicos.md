# 08. Casos prácticos resueltos

**Cómo usar este módulo:** resuelve cada caso en una hoja antes de leer la solución. Compara no solo el número, sino también el asiento, los documentos y la justificación. Si un caso te sale mal, anota el error en tu libro y vuelve al módulo correspondiente.

**Datos generales para todos los casos:**

- UVT 2026: $52.374.
- 2 UVT = $104.748.
- 10 UVT = $523.740.
- IVA general: 19%.
- Retefuente: según concepto y condición del proveedor.
- ReteIVA: 15% del IVA, solo si el comprador es agente.
- ReteICA: solo si el comprador es agente municipal; en los ejemplos se usa 0,966% como tarifa pedagógica de Bogotá.

**Supuestos pedagógicos:** proveedores residentes, facturas válidas, operaciones nacionales, sin notas crédito complejas ni moneda extranjera. Cuando un caso diga “proveedor declarante”, se asume que no es gran contribuyente ni entidad estatal, salvo que se indique lo contrario. Cuando diga “no declarante”, se asume que es responsable de IVA si el caso incluye IVA. Estas simplificaciones no reemplazan la validación del caso real.

---

## Caso 1: servicio general, proveedor declarante, comprador SAS normal

### Datos

- Comprador: SAS normal, agente de retefuente, **no** agente de reteIVA ni de reteICA.
- Proveedor: persona jurídica declarante, no gran contribuyente.
- Servicio general: $2.000.000.
- IVA 19%.
- Retefuente 4%.

### Preguntas

1. ¿Cuál es el IVA?
2. ¿Aplica retefuente? ¿Cuánto?
3. ¿Aplica reteIVA? ¿Aplica reteICA?
4. ¿Cuál es el neto?
5. Registra causación y pago.

### Solución

- IVA: $2.000.000 × 19% = $380.000.
- Total: $2.380.000.
- Base de retefuente: $2.000.000 (sin IVA).
- Mínimo: 2 UVT = $104.748; la base lo supera.
- Retefuente: $2.000.000 × 4% = $80.000.
- ReteIVA: no aplica, porque el comprador no es agente de reteIVA.
- ReteICA: no aplica, porque el comprador no es agente municipal.
- Neto: $2.380.000 − $80.000 = $2.300.000.

### Asiento de causación

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 5135 Servicios | $2.000.000 | |
| 240805 IVA descontable | $380.000 | |
| 220505 Proveedores nacionales | | $2.380.000 |

### Asiento de pago

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 220505 Proveedores nacionales | $2.380.000 | |
| 111005 Bancos | | $2.300.000 |
| 236525 Retención en la fuente — servicios | | $80.000 |

### Documentos

- Factura electrónica validada.
- Certificado de retención por renta (Art. 381 ET).
- Comprobante de egreso y transferencia.
- Formulario 350 del periodo.

### Errores a evitar

- Calcular la retefuente sobre $2.380.000.
- Practicar reteIVA sin ser agente.
- Registrar la retención como gasto.

---

## Caso 2: servicio general, proveedor no declarante

### Datos

- Comprador: SAS normal, agente de retefuente, no agente de reteIVA/reteICA.
- Proveedor: persona natural no declarante, responsable de IVA.
- Servicio general: $500.000.
- IVA 19%.
- Retefuente 6%.

### Solución

- IVA: $95.000.
- Total: $595.000.
- Base: $500.000; mínimo 2 UVT = $104.748; la base lo supera.
- Retefuente: $500.000 × 6% = $30.000.
- ReteIVA: no aplica (comprador no agente).
- Neto: $565.000.

### Asientos

Causación:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 5135 Servicios | $500.000 | |
| 240805 IVA descontable | $95.000 | |
| 220505 Proveedores | | $595.000 |

Pago:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 220505 Proveedores | $595.000 | |
| 111005 Bancos | | $565.000 |
| 236525 Retención en la fuente — servicios | | $30.000 |

### Documentos

- RUT y certificación de no declarante.
- Factura validada.
- Certificado de retención.
- Formulario 350.

### Errores a evitar

- Aplicar 4% en lugar de 6%.
- No documentar la condición de no declarante.

---

## Caso 3: servicio por debajo del mínimo

### Datos

- Comprador: SAS normal.
- Proveedor: persona natural no declarante, responsable de IVA.
- Servicio: $90.000.
- IVA 19%.

### Solución

- IVA: $17.100.
- Total: $107.100.
- Base: $90.000; mínimo 2 UVT = $104.748; la base es inferior.
- Retefuente: $0.
- ReteIVA: $0, aunque el comprador fuera agente, porque la base no supera el mínimo.
- Neto: $107.100.

### Asiento

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 5135 Servicios | $90.000 | |
| 240805 IVA descontable | $17.100 | |
| 111005 Bancos (o proveedores) | | $107.100 |

### Documentos

- Factura validada.
- No hay certificado de retención porque no hubo retención.
- Registro del pago.

### Errores a evitar

- Retener sobre $90.000 “porque es un servicio”.
- Aplicar reteIVA sin verificar el mínimo.
- Fragmentar la operación para evitar la retención.

---

## Caso 4: base exactamente en 2 UVT

### Datos

- Comprador: gran contribuyente (agente de reteIVA).
- Proveedor: persona jurídica declarante, no gran contribuyente.
- Servicio: $104.748 (exactamente 2 UVT).
- IVA 19%.
- Retefuente 4%.
- ReteIVA 15%.

### Solución

- IVA: $104.748 × 19% = $19.902,12.
- Total: $124.650,12.
- Retefuente: $104.748 × 4% = $4.189,92.
- ReteIVA: $19.902,12 × 15% = $2.985,32.
- Neto: $124.650,12 − $4.189,92 − $2.985,32 = $117.474,88.

**Redondeo a peso:** retefuente $4.190; reteIVA $2.985; neto $117.475,12. Define la política y mantén la coherencia.

### Asientos

Causación:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 5135 Servicios | $104.748,00 | |
| 240805 IVA descontable | $19.902,12 | |
| 220505 Proveedores | | $124.650,12 |

Pago:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 220505 Proveedores | $124.650,12 | |
| 111005 Bancos | | $117.474,88 |
| 236525 Retención en la fuente — servicios | | $4.189,92 |
| 236701 Impuesto a las ventas retenido | | $2.985,32 |

### Documentos

- Factura validada.
- Certificado de renta y de IVA.
- Formulario 350.

### Errores a evitar

- No retener porque la base “es igual” al mínimo. La norma dice “inferior a”; igual sí retiene.
- Redondear de forma distinta en el asiento y en el certificado.

---

## Caso 5: honorarios, persona jurídica

### Datos

- Comprador: gran contribuyente (agente de reteIVA).
- Proveedor: persona jurídica declarante, no gran contribuyente.
- Honorarios: $3.000.000.
- IVA 19%.
- Retefuente 11%.
- ReteIVA 15%.

### Solución

- IVA: $570.000.
- Total: $3.570.000.
- Retefuente: $3.000.000 × 11% = $330.000.
- ReteIVA: $570.000 × 15% = $85.500.
- Neto: $3.570.000 − $330.000 − $85.500 = $3.154.500.

### Asientos

Causación:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 5110 Honorarios | $3.000.000 | |
| 240805 IVA descontable | $570.000 | |
| 220505 Proveedores | | $3.570.000 |

Pago:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 220505 Proveedores | $3.570.000 | |
| 111005 Bancos | | $3.154.500 |
| 236515 Retención en la fuente — honorarios | | $330.000 |
| 236701 Impuesto a las ventas retenido | | $85.500 |

### Documentos

- Factura validada.
- Certificado de renta y de IVA.
- Formulario 350.

### Errores a evitar

- Aplicar 10% a una persona jurídica.
- Aplicar el mínimo de servicios a honorarios para retefuente (no tiene mínimo).
- Olvidar la reteIVA si el comprador es agente.

---

## Caso 6: honorarios, persona natural no declarante

### Datos

- Comprador: SAS normal, no agente de reteIVA.
- Proveedor: persona natural no declarante, responsable de IVA.
- Honorarios: $800.000.
- IVA 19%.
- Retefuente 10%.

### Solución

- IVA: $152.000.
- Total: $952.000.
- Retefuente: $800.000 × 10% = $80.000.
- ReteIVA: no aplica (comprador no agente).
- Neto: $872.000.

### Asientos

Causación:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 5110 Honorarios | $800.000 | |
| 240805 IVA descontable | $152.000 | |
| 220505 Proveedores | | $952.000 |

Pago:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 220505 Proveedores | $952.000 | |
| 111005 Bancos | | $872.000 |
| 236515 Retención en la fuente — honorarios | | $80.000 |

### Documentos

- RUT y certificación de no declarante.
- Factura validada.
- Certificado de renta.
- Formulario 350.

### Errores a evitar

- Aplicar 11% sin verificar la excepción de los 3.300 UVT.
- Aplicar el mínimo de servicios a honorarios.

---

## Caso 7: arrendamiento de vivienda

### Datos

- Comprador: SAS normal.
- Proveedor: persona natural declarante, no gran contribuyente.
- Arrendamiento de inmueble para vivienda: $1.200.000.
- IVA: excluido.
- Retefuente 3,5%.

### Solución

- IVA: $0, porque el arrendamiento de vivienda está excluido.
- Total: $1.200.000.
- Mínimo: 10 UVT = $523.740; la base lo supera.
- Retefuente: $1.200.000 × 3,5% = $42.000.
- ReteIVA: no aplica, porque no hay IVA.
- Neto: $1.158.000.

### Asientos

Causación:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 5120 Arrendamientos | $1.200.000 | |
| 220505 Proveedores | | $1.200.000 |

Pago:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 220505 Proveedores | $1.200.000 | |
| 111005 Bancos | | $1.158.000 |
| 236530 Retención en la fuente — arrendamientos | | $42.000 |

### Documentos

- Contrato de arrendamiento.
- Factura o documento equivalente.
- Certificado de retención.
- Formulario 350.

### Errores a evitar

- Aplicar IVA 19% a un arrendamiento de vivienda.
- Aplicar el mínimo de servicios (2 UVT) en lugar del de arrendamiento (10 UVT).
- Confundir arrendamiento de vivienda con arrendamiento comercial.

---

## Caso 8: compra de mercancía, proveedor declarante

### Datos

- Comprador: gran contribuyente (agente de reteIVA).
- Proveedor: persona jurídica declarante, no gran contribuyente.
- Mercancía: $4.000.000.
- IVA 19%.
- Retefuente 2,5%.
- ReteIVA 15%.

### Solución

- IVA: $760.000.
- Total: $4.760.000.
- Mínimo: 10 UVT = $523.740; la base lo supera.
- Retefuente: $4.000.000 × 2,5% = $100.000.
- ReteIVA: $760.000 × 15% = $114.000.
- Neto: $4.546.000.

### Asientos

Causación:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 143505 Inventarios | $4.000.000 | |
| 240805 IVA descontable | $760.000 | |
| 220505 Proveedores | | $4.760.000 |

Pago:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 220505 Proveedores | $4.760.000 | |
| 111005 Bancos | | $4.546.000 |
| 236540 Retención en la fuente — compras | | $100.000 |
| 236701 Impuesto a las ventas retenido | | $114.000 |

### Documentos

- Factura validada.
- Certificado de renta y de IVA.
- Formulario 350.
- Inventario y acta de recibido.

### Errores a evitar

- Usar la tarifa de servicios (4%/6%) en una compra.
- Calcular retefuente sobre $4.760.000.
- Olvidar que el IVA va a inventario, no a gasto.

---

## Caso 9: compra de mercancía, proveedor no declarante

### Datos

- Comprador: SAS normal, no agente de reteIVA.
- Proveedor: persona natural no declarante, responsable de IVA.
- Mercancía: $1.000.000.
- IVA 19%.
- Retefuente 3,5%.

### Solución

- IVA: $190.000.
- Total: $1.190.000.
- Mínimo: 10 UVT = $523.740; la base lo supera.
- Retefuente: $1.000.000 × 3,5% = $35.000.
- ReteIVA: no aplica (comprador no agente).
- Neto: $1.155.000.

### Asientos

Causación:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 143505 Inventarios | $1.000.000 | |
| 240805 IVA descontable | $190.000 | |
| 220505 Proveedores | | $1.190.000 |

Pago:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 220505 Proveedores | $1.190.000 | |
| 111005 Bancos | | $1.155.000 |
| 236540 Retención en la fuente — compras | | $35.000 |

### Documentos

- RUT y certificación de no declarante.
- Factura validada.
- Certificado de renta.
- Formulario 350.

### Errores a evitar

- Aplicar 2,5% a un no declarante.
- No verificar el mínimo de 10 UVT.

---

## Caso 10: gran contribuyente, servicio

### Datos

- Comprador: gran contribuyente (agente de reteIVA).
- Proveedor: persona jurídica declarante, no gran contribuyente.
- Servicio: $5.000.000.
- IVA 19%.
- Retefuente 4%.
- ReteIVA 15%.

### Solución

- IVA: $950.000.
- Total: $5.950.000.
- Retefuente: $200.000.
- ReteIVA: $142.500.
- Neto: $5.607.500.

### Asientos

Causación:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 5135 Servicios | $5.000.000 | |
| 240805 IVA descontable | $950.000 | |
| 220505 Proveedores | | $5.950.000 |

Pago:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 220505 Proveedores | $5.950.000 | |
| 111005 Bancos | | $5.607.500 |
| 236525 Retención en la fuente — servicios | | $200.000 |
| 236701 Impuesto a las ventas retenido | | $142.500 |

### Documentos

- Factura validada.
- Certificado de renta y de IVA.
- Formulario 350.

### Errores a evitar

- No practicar reteIVA entre agentes excluidos (entidades estatales, grandes contribuyentes o emisoras de tarjetas). Aquí el proveedor no es gran contribuyente, así que la retención procede.
- Olvidar que la reteIVA la practica el comprador, no el vendedor.

---

## Caso 11: reteICA en Bogotá

### Datos

- Comprador: SAS normal, **agente de reteICA** designado en Bogotá, no agente de reteIVA.
- Proveedor: persona jurídica declarante, no gran contribuyente.
- Servicio: $2.000.000.
- IVA 19%.
- Retefuente 4%.
- ReteICA: 0,966% (ejemplo pedagógico; verifica la tarifa vigente y la reforma de 2026).

### Solución

- IVA: $380.000.
- Total: $2.380.000.
- Retefuente: $80.000.
- ReteICA: $2.000.000 × 0,966% = $19.320.
- ReteIVA: no aplica.
- Neto: $2.280.680.

### Asientos

Causación:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 5135 Servicios | $2.000.000 | |
| 240805 IVA descontable | $380.000 | |
| 220505 Proveedores | | $2.380.000 |

Pago:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 220505 Proveedores | $2.380.000 | |
| 111005 Bancos | | $2.280.680 |
| 236525 Retención en la fuente — servicios | | $80.000 |
| 2368 Impuesto de industria y comercio retenido | | $19.320 |

Pago de reteICA:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 2368 Impuesto de industria y comercio retenido | $19.320 | |
| 111005 Bancos | | $19.320 |

### Documentos

- Factura validada.
- Certificado de renta.
- Certificado de reteICA.
- Formulario 350 (solo renta/IVA).
- Declaración municipal de reteICA.

### Errores a evitar

- Incluir la reteICA en el Formulario 350.
- Aplicar la tarifa del comprador en lugar de la actividad del vendedor.
- Usar una tarifa de Bogotá sin verificar la vigencia y la reforma.

---

## Caso 12: proveedor SIMPLE

### Datos

- Comprador: gran contribuyente (agente de reteIVA).
- Proveedor: contribuyente del SIMPLE, responsable de IVA.
- Servicio: $1.000.000.
- IVA 19%.
- Retefuente: no aplica.
- ReteICA: no aplica.
- ReteIVA 15%.

### Solución

- IVA: $190.000.
- Total: $1.190.000.
- Retefuente: $0 (Art. 911 ET).
- ReteICA: $0.
- ReteIVA: $190.000 × 15% = $28.500.
- Neto: $1.161.500.

### Asientos

Causación:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 5135 Servicios | $1.000.000 | |
| 240805 IVA descontable | $190.000 | |
| 220505 Proveedores | | $1.190.000 |

Pago:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 220505 Proveedores | $1.190.000 | |
| 111005 Bancos | | $1.161.500 |
| 236701 Impuesto a las ventas retenido | | $28.500 |

### Documentos

- RUT con código 47.
- Factura validada.
- Certificado de reteIVA.
- Formulario 350.
- No hay certificado de renta porque no hubo retención.

### Errores a evitar

- Practicar retefuente a un SIMPLE.
- Practicar reteICA a un SIMPLE.
- Olvidar la reteIVA si el proveedor es responsable de IVA y el comprador es agente.

---

## Caso 13: proveedor autorretenedor

### Datos

- Comprador: gran contribuyente (agente de reteIVA).
- Proveedor: autorretenedor de renta, no gran contribuyente.
- Servicio: $1.000.000.
- IVA 19%.
- Retefuente: no aplica.
- ReteIVA 15%.

### Solución

- IVA: $190.000.
- Total: $1.190.000.
- Retefuente: $0; el proveedor se autorretiene.
- ReteIVA: $28.500.
- Neto: $1.161.500.

### Asientos

Causación:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 5135 Servicios | $1.000.000 | |
| 240805 IVA descontable | $190.000 | |
| 220505 Proveedores | | $1.190.000 |

Pago:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 220505 Proveedores | $1.190.000 | |
| 111005 Bancos | | $1.161.500 |
| 236701 Impuesto a las ventas retenido | | $28.500 |

### Documentos

- Autorización de autorretención.
- Factura validada.
- Certificado de reteIVA.
- Formulario 350.

### Errores a evitar

- Practicar retefuente a un autorretenedor.
- No guardar la autorización.
- Confundir autorretención con “no retención” de IVA.

---

## Caso 14: factura con IVA incluido

### Datos

- Comprador: SAS normal.
- Proveedor: persona jurídica declarante, no gran contribuyente.
- Total facturado: $1.190.000, con IVA 19% incluido.
- Retefuente 4%.

### Solución

- Base: $1.190.000 / 1,19 = $1.000.000.
- IVA: $190.000.
- Retefuente: $1.000.000 × 4% = $40.000.
- Neto: $1.150.000.

### Asientos

Causación:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 5135 Servicios | $1.000.000 | |
| 240805 IVA descontable | $190.000 | |
| 220505 Proveedores | | $1.190.000 |

Pago:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 220505 Proveedores | $1.190.000 | |
| 111005 Bancos | | $1.150.000 |
| 236525 Retención en la fuente — servicios | | $40.000 |

### Documentos

- Factura validada, con base e IVA discriminados.
- Certificado de retención.
- Formulario 350.

### Errores a evitar

- Calcular la retefuente sobre el total de $1.190.000.
- Asumir que el total es la base.
- No verificar la tarifa del IVA.

---

## Caso 15: pago parcial

### Datos

- Comprador: gran contribuyente (agente de reteIVA).
- Proveedor: persona jurídica declarante, no gran contribuyente.
- Factura: base $1.000.000 + IVA $190.000 = $1.190.000.
- Retefuente 4%: $40.000.
- ReteIVA 15%: $28.500.
- Se paga el 50%.

### Solución

- Base del pago: $500.000.
- IVA del pago: $95.000.
- Total del pago: $595.000.
- Retefuente del pago: $500.000 × 4% = $20.000.
- ReteIVA del pago: $95.000 × 15% = $14.250.
- Neto del pago: $595.000 − $20.000 − $14.250 = $560.750.
- Saldo del proveedor: $595.000.
- Retención pendiente: $20.000 de renta y $14.250 de IVA.

### Asiento de pago

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 220505 Proveedores | $595.000 | |
| 111005 Bancos | | $560.750 |
| 236525 Retención en la fuente — servicios | | $20.000 |
| 236701 Impuesto a las ventas retenido | | $14.250 |

### Documentos

- Factura validada.
- Certificado de retención por el pago parcial.
- Comprobante de pago.
- Formulario 350 del periodo.

### Errores a evitar

- Retener sobre el total de la factura cuando solo se paga una parte.
- No verificar el mínimo en cada pago.
- No dejar constancia del saldo pendiente.

---

## Caso 16: nota crédito antes del pago

### Datos

- Comprador: SAS normal.
- Proveedor: persona jurídica declarante, no gran contribuyente.
- Factura original: base $2.000.000 + IVA $380.000 = $2.380.000.
- Retefuente 4%: $80.000.
- Nota crédito del 50% antes del pago.

### Solución

- Base de la nota crédito: $1.000.000.
- IVA: $190.000.
- Total de la nota crédito: $1.190.000.
- Retefuente que se reversa: $40.000.
- Saldo de la factura después de la nota: $1.190.000.
- Retefuente sobre el saldo: $40.000.
- Neto a pagar: $1.150.000.

### Asientos

Nota crédito:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 220505 Proveedores | $1.190.000 | |
| 5135 Servicios | | $1.000.000 |
| 240805 IVA descontable | | $190.000 |

Pago del saldo:

| Cuenta | Débito | Crédito |
|---|---:|---:|
| 220505 Proveedores | $1.190.000 | |
| 111005 Bancos | | $1.150.000 |
| 236525 Retención en la fuente — servicios | | $40.000 |

### Documentos

- Nota crédito validada, que referencia la factura original.
- Certificado de retención por el saldo.
- Formulario 350.

### Errores a evitar

- No reversar el IVA.
- No ajustar la retención.
- Si la factura ya se pagó, no “borrar” la retención declarada; ajustar en el siguiente periodo.

---

## Caso integral: expediente completo

Toma el Caso 1 y arma el expediente:

| Documento | Estado | Observación |
|---|---|---|
| RUT del proveedor | Sí | Código 05, 42, 48. |
| Certificado de existencia | Sí | Representante legal vigente. |
| Orden de compra | Sí | Autorizada. |
| Factura electrónica | Sí | Validada, CUFE, base e IVA discriminados. |
| Acta de recibido | Sí | Servicio prestado. |
| Asiento de causación | Sí | Débitos = créditos. |
| Pago | Sí | Neto $2.300.000. |
| Certificado de retención | Sí | $80.000, concepto servicios. |
| Formulario 350 | Sí | Incluye la retención. |
| Archivo | Sí | XML, PDF, comprobante, certificado. |

**Pregunta de cierre:** si el proveedor te pidiera el certificado antes de marzo, ¿puedes emitirlo? Sí, el plazo es máximo, no mínimo. Lo importante es que los datos coincidan con la declaración.

---

## Tabla resumen de los 16 casos

| Caso | Concepto | Base | IVA | Retefuente | ReteIVA | ReteICA | Neto |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 | Servicio declarante | $2.000.000 | $380.000 | $80.000 | $0 | $0 | $2.300.000 |
| 2 | Servicio no declarante | $500.000 | $95.000 | $30.000 | $0 | $0 | $565.000 |
| 3 | Servicio bajo mínimo | $90.000 | $17.100 | $0 | $0 | $0 | $107.100 |
| 4 | Servicio en 2 UVT | $104.748 | $19.902,12 | $4.189,92 | $2.985,32 | $0 | $117.474,88 |
| 5 | Honorarios jurídicos | $3.000.000 | $570.000 | $330.000 | $85.500 | $0 | $3.154.500 |
| 6 | Honorarios no declarante | $800.000 | $152.000 | $80.000 | $0 | $0 | $872.000 |
| 7 | Arrendamiento vivienda | $1.200.000 | $0 | $42.000 | $0 | $0 | $1.158.000 |
| 8 | Compra declarante | $4.000.000 | $760.000 | $100.000 | $114.000 | $0 | $4.546.000 |
| 9 | Compra no declarante | $1.000.000 | $190.000 | $35.000 | $0 | $0 | $1.155.000 |
| 10 | Gran contribuyente | $5.000.000 | $950.000 | $200.000 | $142.500 | $0 | $5.607.500 |
| 11 | ReteICA Bogotá | $2.000.000 | $380.000 | $80.000 | $0 | $19.320 | $2.280.680 |
| 12 | SIMPLE | $1.000.000 | $190.000 | $0 | $28.500 | $0 | $1.161.500 |
| 13 | Autorretenedor | $1.000.000 | $190.000 | $0 | $28.500 | $0 | $1.161.500 |
| 14 | Total con IVA | $1.000.000 | $190.000 | $40.000 | $0 | $0 | $1.150.000 |
| 15 | Pago parcial 50% | $500.000 | $95.000 | $20.000 | $14.250 | $0 | $560.750 |
| 16 | Nota crédito 50% | $1.000.000 | $190.000 | $40.000 | $0 | $0 | $1.150.000 |

**Nota:** la tabla muestra la base y los impuestos de la operación o de la parte pagada, según el caso. En el caso 16, la base es la que queda después de la nota crédito.

---

## Cómo calificar tus respuestas

| Nivel | Criterio |
|---|---|
| Excelente | Cálculo correcto, asiento correcto, documentos completos y justificación legal. |
| Bueno | Cálculo correcto, asiento correcto, pero falta un documento o una explicación. |
| Aceptable | Cálculo correcto, pero el asiento tiene un error de cuenta o de naturaleza. |
| Insuficiente | Error de base, tarifa, mínimo o agente; no entiende por qué. |

Si tienes más de dos casos “insuficientes”, vuelve a los módulos 04, 05 y 06 antes de seguir.
