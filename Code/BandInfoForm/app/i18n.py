"""Bilingual strings for the public band-advance form + thanks page.

One table, two languages, short symbolic keys — form.html/thanks.html call
`t('key')` instead of carrying literal copy, so English and Spanish can never
drift apart silently (add a key here, reference it there). `lang` is just
'en' or 'es'; anything else falls back to 'en'. A missing key falls back to
the key itself (visible in the browser, easy to spot) rather than raising.

This covers DISPLAY TEXT only — labels, help, options, buttons. Field
`name=` attributes and stored option `value=`s stay in English on both
language variants of the form, so the database/docfill/daysheet pipeline
never has to know or care which language a band filled the form in. Only
the free-text fields (textareas) carry actual Spanish content through the
pipeline — that's handled separately at submit time, not here.

Venue-specific email copy (the FSQ advance email) is a different table —
see venue_email.py's VENUE_EMAIL / VENUE_EMAIL_ES.
"""

STRINGS = {
    # ── page chrome ──────────────────────────────────────────────────────
    "page_title":        {"en": "3CDC Band Advance", "es": "Avance de banda — 3CDC"},
    "header_h1":         {"en": "Band Advance / Show Details",
                           "es": "Avance de banda / Detalles del show"},
    "intro_default":     {"en": "Please complete this so we have everything we need to run your show.",
                           "es": "Por favor completen esto para que tengamos todo lo necesario para su show."},
    "techpack_link":     {"en": "See what 3CDC provides at this venue →",
                           "es": "Vea lo que 3CDC proporciona en este lugar →"},
    "lang_toggle":        {"en": "Español", "es": "English"},

    "returning_banner":  {"en": "Welcome back{artist_clause}. We've pre-filled your last submission "
                                 "below — update anything that has changed and re-acknowledge the "
                                 "items at the bottom. Fields marked “locked to your booking” "
                                 "are set from our records; email us if one of those is wrong.",
                           "es": "Bienvenidos de nuevo{artist_clause}. Ya completamos el formulario a "
                                 "continuación con los datos de su show anterior — actualicen lo "
                                 "que haya cambiado y vuelvan a confirmar los puntos al final. Los campos "
                                 "marcados “bloqueado a su reserva” están definidos según "
                                 "nuestros registros; escríbannos si alguno de esos datos está "
                                 "incorrecto."},
    "returning_artist_clause": {"en": ", {name}", "es": ", {name}"},

    # ── section headers ──────────────────────────────────────────────────
    "section_basics":     {"en": "Show Basics", "es": "Datos básicos del show"},
    "section_technical":  {"en": "Stage & Technical", "es": "Escenario y aspectos técnicos"},
    "section_hospitality": {"en": "Hospitality & Site", "es": "Hospitalidad y sitio"},
    "section_ack":        {"en": "Acknowledgments", "es": "Confirmaciones"},

    # ── changed-notes (returning artist only) ───────────────────────────
    "changed_notes_label": {"en": "Anything changed since your last show with us?",
                             "es": "¿Algo cambió desde su último show con nosotros?"},
    "changed_notes_placeholder": {"en": "e.g. added a keyboard player, different monitor mix, new stage plot",
                                   "es": "p. ej. se agregó un tecladista, mezcla de monitores diferente, "
                                         "nuevo plano de escenario"},
    "changed_notes_help": {"en": "If your setup is the same as last time, leave this blank. Otherwise tell "
                                  "us what's different — lineup, gear, monitors, stage plot.",
                            "es": "Si su configuración es igual a la vez anterior, dejen esto en "
                                  "blanco. De lo contrario, indiquen qué es diferente — "
                                  "integrantes, equipo, monitores, plano de escenario."},

    # ── show basics ──────────────────────────────────────────────────────
    "band_name_label":   {"en": "Band / Group Name", "es": "Nombre de la banda / grupo"},
    "band_name_prefill_help": {"en": "Prefilled from your booking — update it if this has changed.",
                                "es": "Completado previamente según su reserva — actualícenlo "
                                      "si esto ha cambiado."},
    "venue_label":       {"en": "Venue", "es": "Lugar"},
    "select_placeholder": {"en": "Select…", "es": "Seleccione…"},
    "select_venue_placeholder": {"en": "Select a venue…", "es": "Seleccione un lugar…"},
    "lockhint":          {"en": "🔒 Locked to your booking — email us if this needs to change.",
                           "es": "🔒 Bloqueado según su reserva — escríbannos si "
                                 "esto necesita cambiar."},
    "show_date_label":   {"en": "Show Date", "es": "Fecha del show"},
    "contact_name_label": {"en": "Primary Contact — name", "es": "Contacto principal — nombre"},
    "contact_name_help": {"en": "Who we should reach for anything about this show.",
                           "es": "La persona con quien debemos comunicarnos para cualquier asunto "
                                 "relacionado con este show."},
    "contact_email_label": {"en": "Primary Contact — email", "es": "Contacto principal — correo electrónico"},
    "contact_phone_label": {"en": "Primary Contact — best day-of cell phone",
                             "es": "Contacto principal — mejor número de celular para el día del evento"},
    "contact_phone_help": {"en": "Best point of contact from the group on show day — our on-site "
                                  "techs use this number to reach you if you're running late or need to "
                                  "be located.",
                            "es": "El mejor punto de contacto del grupo el día del show — "
                                  "nuestro equipo técnico en el sitio usa este número para "
                                  "comunicarse con ustedes si van tarde o si necesitamos ubicarlos."},

    # ── stage & technical ────────────────────────────────────────────────
    "stage_plot_upload_label": {"en": "Stage Plot / Input List — upload",
                                 "es": "Plano de escenario / lista de entradas — subir archivo"},
    "stage_plot_upload_help": {"en": "Please provide a current stage plot / input list — this upload "
                                      "or the description below, at least one is required.",
                                "es": "Por favor proporcionen un plano de escenario / lista de entradas "
                                      "actualizado — ya sea este archivo o la descripción a "
                                      "continuación; se requiere al menos uno."},
    "stage_plot_upload_existing": {"en": " We have one on file from last time — only upload if it "
                                          "has changed.",
                                    "es": " Tenemos uno registrado de la vez anterior — suban "
                                          "uno nuevo solo si ha cambiado."},
    "stage_plot_desc_label": {"en": "Stage Plot / Input List — description or link",
                               "es": "Plano de escenario / lista de entradas — descripción o enlace"},
    "stage_plot_desc_help": {"en": "Describe your input list / stage layout, or paste a link — "
                                    "required only if you didn't upload a file above.",
                              "es": "Describan su lista de entradas / distribución del escenario, o "
                                    "peguen un enlace — obligatorio solo si no subieron un archivo "
                                    "arriba."},
    "stage_type_label": {"en": "Would you prefer a flat stage or a drum riser?",
                          "es": "¿Prefieren un escenario plano o una plataforma para la batería?"},
    "stage_type_flat":   {"en": "Flat stage", "es": "Escenario plano"},
    "stage_type_riser":  {"en": "Drum riser", "es": "Plataforma para batería"},
    "monitors_label":    {"en": "How many monitors do you need?", "es": "¿Cuántos monitores necesitan?"},
    "monitors_cap_help": {"en": "This location ({location}) is limited to {cap} monitor{plural}.",
                           "es": "Este lugar ({location}) está limitado a {cap} monitor{plural}."},
    "uses_iems_label":   {"en": "Do you use in-ear monitors?",
                           "es": "¿Usan monitores intraauriculares (IEM)?"},
    "yes":               {"en": "Yes", "es": "Sí"},
    "no":                {"en": "No", "es": "No"},
    "iem_count_label":   {"en": "How many in-ear systems do you need?",
                           "es": "¿Cuántos sistemas de monitores intraauriculares necesitan?"},
    "own_iems_label":    {"en": "Are you bringing your own in-ear system?",
                           "es": "¿Van a traer su propio sistema de monitores intraauriculares?"},
    "split_snake_label": {"en": "Are you providing a split snake for front of house?",
                           "es": "¿Van a proporcionar un split (snake) para el FOH?"},
    "split_snake_help":  {"en": "Since you're bringing your own in-ear system, let us know if you're "
                                 "providing the split.",
                           "es": "Como van a traer su propio sistema de IEM, indiquen si van a "
                                 "proporcionar el split."},
    "backline_label":    {"en": "Backline / Instrumentation — are you sharing with another artist "
                                 "on the event?",
                           "es": "Backline / instrumentación — ¿van a compartir con otro "
                                 "artista del evento?"},
    "backline_help":     {"en": "Artists provide all instruments, including amps and 1/4-inch cables. If "
                                 "you've coordinated to share backline with another artist on the event, "
                                 "note it here.",
                           "es": "Los artistas proporcionan todos los instrumentos, incluyendo "
                                 "amplificadores y cables de 1/4 de pulgada. Si coordinaron compartir el "
                                 "backline con otro artista del evento, indíquenlo aquí."},
    "own_engineer_label": {"en": "Are you bringing your own sound engineer?",
                            "es": "¿Van a traer su propio ingeniero de sonido?"},
    "own_engineer_no":   {"en": "No — use house engineers", "es": "No — usar los ingenieros de la casa"},
    "own_engineer_yes":  {"en": "Yes — bringing our own (we'll coordinate)",
                           "es": "Sí — vamos a traer el nuestro (coordinaremos)"},
    "own_engineer_help": {"en": "We provide audio engineers to mix FOH and monitors. If you plan to "
                                 "bring your own, please coordinate in advance. All engineers must mix "
                                 "within the 95 dBA-Slow ordinance; the 3CDC engineer reserves the right "
                                 "to baffle amps to reduce stage volume if necessary.",
                           "es": "Proporcionamos ingenieros de audio para mezclar el FOH y los "
                                 "monitores. Si planean traer el suyo, por favor coordinen con "
                                 "anticipación. Todos los ingenieros deben mezclar dentro del "
                                 "límite de la ordenanza de 95 dBA-Slow; el ingeniero de 3CDC se "
                                 "reserva el derecho de reducir el volumen de los amplificadores en el "
                                 "escenario si es necesario."},
    "scenic_label":      {"en": "Do you have a backdrop or any scenic elements we should be aware of?",
                           "es": "¿Tienen algún telón de fondo o elemento escenográfico "
                                 "que debamos saber?"},
    "lighting_label":    {"en": "Lighting requests", "es": "Solicitudes de iluminación"},
    "lighting_help":     {"en": "We provide a house LD. Let us know any specific requests and we'll do "
                                 "our best to accommodate.",
                           "es": "Proporcionamos un LD (diseñador de iluminación) de la casa. "
                                 "Indiquen cualquier solicitud específica y haremos lo posible por "
                                 "atenderla."},

    # ── hospitality & site ───────────────────────────────────────────────
    "merch_label":       {"en": "Are you selling merch?", "es": "¿Van a vender mercancía?"},
    "merch_help":        {"en": "If yes, you're responsible for providing a seller, point of sale, and "
                                 "bank. We provide a tent next to the stage with a table and chairs.",
                           "es": "Si es así, son responsables de proporcionar al vendedor, el punto "
                                 "de venta y el banco. Nosotros proporcionamos una carpa junto al "
                                 "escenario con una mesa y sillas."},
    "band_tent_label":   {"en": "Do you want a private band tent? (10×10 with sidewalls)",
                           "es": "¿Desean una carpa privada para la banda? (10×10 con paredes "
                                 "laterales)"},
    "band_tent_yes":     {"en": "Yes, please provide the tent", "es": "Sí, por favor proporcionen la carpa"},
    "band_tent_no":      {"en": "No, not needed", "es": "No, no es necesario"},
    "band_tent_help":    {"en": "We do not have indoor dressing rooms. On request we can provide a "
                                 "10×10 tent with sidewalls for private band space.",
                           "es": "No contamos con camerinos bajo techo. A solicitud, podemos "
                                 "proporcionar una carpa de 10×10 con paredes laterales para un "
                                 "espacio privado de la banda."},
    "performers_label":  {"en": "Total number of performers and crew",
                           "es": "Número total de artistas y equipo de trabajo"},
    "performers_help":   {"en": "Drink tickets and water are provided for all performers and crew.",
                           "es": "Se proporcionan boletos de bebida y agua para todos los artistas y el "
                                 "equipo de trabajo."},
    "vehicle_count_label": {"en": "How many vehicles will you be arriving in?",
                             "es": "¿Con cuántos vehículos llegarán?"},
    "vehicle_count_help": {"en": "Total vehicles for your whole group — this is how many parking "
                                  "garage validations we prepare for you.",
                            "es": "Total de vehículos de todo su grupo — así sabemos cuántas "
                                  "validaciones de estacionamiento preparar para ustedes."},
    "large_vehicle_label": {"en": "Do you need large vehicle parking?",
                             "es": "¿Necesitan estacionamiento para vehículo grande?"},
    "large_vehicle_help": {"en": "Includes any vehicle over 6 ft 8 in (the garage "
                                  "clearance), large vans, any vehicle with a trailer, and tour buses.",
                            "es": "Incluye cualquier vehículo de más de 6 pies 8 pulgadas (la "
                                  "altura máxima del estacionamiento), camionetas grandes, cualquier "
                                  "vehículo con remolque y autobuses de gira."},

    # ── acknowledgments ──────────────────────────────────────────────────
    "ack_loadin_text":   {"en": "The load-in process at 3CDC has changed — please review the "
                                 "document your contact sent. Each vehicle needs its own parking QR "
                                 "validation before arriving; scan at the kiosk on entry or exit (please "
                                 "don't pay).",
                           "es": "El proceso de carga en 3CDC ha cambiado — por favor revisen el "
                                 "documento que les envió su contacto. Cada vehículo necesita su "
                                 "propia validación de estacionamiento con código QR antes de "
                                 "llegar; escaneen en el quiosco al entrar o salir (por favor no "
                                 "paguen)."},
    "ack_loadin_check":  {"en": "I have reviewed the load-in document.",
                           "es": "He revisado el documento de carga."},
    "ack_95db_text":     {"en": "We're required by the city to maintain a strict 95 dBA-Slow limit, "
                                 "measured at the FOH position. All engineers (house or talent) are held "
                                 "to that level.",
                           "es": "La ciudad nos exige mantener un límite estricto de 95 dBA-Slow, "
                                 "medido en la posición de FOH. Todos los ingenieros (de la casa o "
                                 "del talento) deben respetar ese nivel."},
    "ack_95db_check":    {"en": "I understand and acknowledge the 95 dBA-Slow limit.",
                           "es": "Entiendo y acepto el límite de 95 dBA-Slow."},
    "ack_reqs_intro":    {"en": "Failure to comply with the below may result in a warning or termination "
                                 "of the show, with payment canceled or delayed. Please read and "
                                 "acknowledge:",
                           "es": "El incumplimiento de lo siguiente puede resultar en una advertencia o "
                                 "en la cancelación del show, con el pago suspendido o retrasado. "
                                 "Por favor lean y confirmen:"},
    "ack_reqs_content":  {"en": "<b>Content:</b> Family-friendly only — no foul language or "
                                 "gestures. Applies to prerecorded tracks, live vocals, and sound check.",
                           "es": "<b>Contenido:</b> solo apto para toda la familia — no se permite "
                                 "lenguaje ni gestos obscenos. Aplica a pistas pregrabadas, voces en vivo "
                                 "y la prueba de sonido."},
    "ack_reqs_sound":    {"en": "<b>Sound limit:</b> Strict 95 dBA-Slow at FOH for all engineers, house "
                                 "or talent.",
                           "es": "<b>Límite de sonido:</b> estricto 95 dBA-Slow en el FOH, para "
                                 "todos los ingenieros, de la casa o del talento."},
    "ack_reqs_performer": {"en": "<b>Performer safety:</b> Stay on the stage. No crowd surfing, "
                                  "climbing, jumping off stage, or stepping on sound equipment.",
                            "es": "<b>Seguridad de los artistas:</b> permanezcan en el escenario. No se "
                                  "permite lanzarse al público, trepar, saltar del escenario ni pisar "
                                  "el equipo de sonido."},
    "ack_reqs_audience": {"en": "<b>Audience safety:</b> Do not throw or shoot anything into the crowd "
                                 "(confetti, t-shirts, bottles, merch/CDs, etc.).",
                           "es": "<b>Seguridad del público:</b> no lancen ni disparen nada hacia el "
                                 "público (confeti, camisetas, botellas, mercancía/CDs, etc.)."},
    "ack_reqs_weather":  {"en": "<b>Weather:</b> Rain or shine. Booking evaluates weather about 3 hours "
                                 "before start. If you don't hear otherwise, assume the show goes on.",
                           "es": "<b>Clima:</b> el show se realiza con lluvia o con sol. El equipo de "
                                 "producción evalúa las condiciones climáticas "
                                 "aproximadamente 3 horas antes del inicio. Si no reciben aviso "
                                 "contrario, asuman que el show continúa."},
    "ack_reqs_payment":  {"en": "<b>Payment:</b> All groups are paid after the performance, not before.",
                           "es": "<b>Pago:</b> todos los grupos reciben su pago después de la "
                                 "presentación, no antes."},
    "ack_reqs_check":    {"en": "I have read and acknowledge all performance requirements.",
                           "es": "He leído y acepto todos los requisitos de la presentación."},

    "additional_label":  {"en": "Additional questions or concerns?",
                           "es": "¿Preguntas o inquietudes adicionales?"},
    "submit_button":     {"en": "Submit show details", "es": "Enviar detalles del show"},

    # ── thanks page ──────────────────────────────────────────────────────
    "thanks_title":      {"en": "Thank you", "es": "Gracias"},
    "thanks_body":       {"en": "We have your show details. Your booking contact will follow up if "
                                 "anything is missing.",
                           "es": "Ya tenemos los detalles de su show. Su contacto de reserva se "
                                 "comunicará si falta algo."},
}


def t(key, lang="en", **kw):
    """Look up `key` in STRINGS for `lang` ('en'/'es', anything else -> 'en'),
    falling back to 'en' if the key exists but not in that language, and to
    the literal key (visibly wrong, not a crash) if it doesn't exist at all.
    kw is applied via str.format for the handful of parametrized strings
    (monitor cap, returning-artist name clause, etc.)."""
    lang = lang if lang == "es" else "en"
    entry = STRINGS.get(key)
    if entry is None:
        return key
    text = entry.get(lang, entry.get("en", key))
    if kw:
        try:
            text = text.format(**kw)
        except (KeyError, IndexError):
            pass
    return text


def translator(lang):
    """Bind a `t(key, **kw)` callable to one request's language, for
    render_template(..., t=translator(lang))."""
    def _t(key, **kw):
        return t(key, lang, **kw)
    return _t
