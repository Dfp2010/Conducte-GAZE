# ─────────────────────────────────────────────────────────────
LAYER_NAME  = "Extinderi retele gaze Total"
OUTPUT_NAME = "Conducte-GAZE.geojson"
# ─────────────────────────────────────────────────────────────

def openProject():
    pass


def saveProject():
    import qgis.core as qc
    import qgis.utils
    import os, json

    iface     = qgis.utils.iface
    project   = qc.QgsProject.instance()
    proj_path = project.homePath()

    def msg(text, lvl=1, dur=5):
        iface.messageBar().pushMessage("Export", text, level=lvl, duration=dur)

    if not proj_path:
        msg("Salveaza proiectul intr-un folder mai intai!")
        return

    layers = project.mapLayersByName(LAYER_NAME)
    if not layers:
        msg("Layer '%s' nu a fost gasit!" % LAYER_NAME)
        return

    layer   = layers[0]
    src_crs = layer.crs()
    dst_crs = qc.QgsCoordinateReferenceSystem("EPSG:4326")
    ctx     = qc.QgsCoordinateTransformContext()
    xform   = qc.QgsCoordinateTransform(src_crs, dst_crs, ctx)

    def clean(v):
        """Converteste valorile QGIS in tipuri JSON-safe."""
        try:
            if v is None or v == qc.NULL:
                return None
        except Exception:
            pass
        if isinstance(v, (int, float, str, bool)):
            return v
        return str(v)

    field_names = [f.name() for f in layer.fields()]
    features    = []

    for feat in layer.getFeatures():
        geom = feat.geometry()
        if geom is None or geom.isEmpty():
            continue

        # ── Coordonate ORIGINALE (CRS-ul layerului = Stereo70) ──
        if geom.isMultipart():
            parts_src = geom.asMultiPolyline()
        else:
            parts_src = [geom.asPolyline()]

        st70 = [[[round(p.x(), 3), round(p.y(), 3)] for p in part]
                for part in parts_src if len(part) >= 2]

        if not st70:
            continue

        # ── Geometrie reproiectata pentru harta (WGS84) ──
        g2 = qc.QgsGeometry(geom)
        g2.transform(xform)

        if g2.isMultipart():
            gtype  = "MultiLineString"
            coords = [[[round(p.x(), 8), round(p.y(), 8)] for p in part]
                      for part in g2.asMultiPolyline()]
        else:
            gtype  = "LineString"
            coords = [[round(p.x(), 8), round(p.y(), 8)] for p in g2.asPolyline()]

        props = {name: clean(feat[name]) for name in field_names}
        props["_st70"] = st70

        features.append({
            "type":       "Feature",
            "geometry":   {"type": gtype, "coordinates": coords},
            "properties": props
        })

    geojson = {
        "type": "FeatureCollection",
        "crs":  {"type": "name",
                 "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": features
    }

    output_path = os.path.join(proj_path, OUTPUT_NAME)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(geojson, f, ensure_ascii=False, separators=(",", ":"))
        msg("%s actualizat (%d entitati, cu coordonate Stereo70)"
            % (OUTPUT_NAME, len(features)), lvl=3, dur=4)
    except Exception as e:
        msg("Eroare la scriere: %s" % e, lvl=2, dur=8)


def closeProject():
    pass
