/**
 * extract_kv_elements.jsx — Extrai assets do KV: artboards + camadas categorizadas.
 *
 * Executado via COM (app.DoJavaScript) pelo wrapper Python.
 * CONFIG_PATH e injetada pelo Python antes da execucao.
 *
 * Config JSON esperado:
 * {
 *   "output_dir": "G:/path/to/KV",
 *   "artboard_dpi": 300,
 *   "categories": {
 *     "logos":    ["logo", "logotipo", "marca", "simbolo", "brand"],
 *     "elementos": ["elemento", "detalhe", "grafismo", "icone", "pattern"],
 *     "fundos":   ["fundo", "background", "bg", "base"]
 *   }
 * }
 */

// CONFIG_PATH is injected by Python wrapper before execution
// var CONFIG_PATH = "C:/path/to/extract_config.json";

// ── Helpers ───────────────────────────────────────────────────────────────────

function readJSON(filePath) {
    var f = new File(filePath);
    if (!f.exists) throw new Error("Config not found: " + filePath);
    f.open("r");
    f.encoding = "UTF-8";
    var raw = f.read();
    f.close();
    return eval("(" + raw + ")");
}

function writeJSON(filePath, obj) {
    var f = new File(filePath);
    f.open("w");
    f.encoding = "UTF-8";
    f.write(jsonStringify(obj));
    f.close();
}

function jsonStringify(obj) {
    if (obj === null || obj === undefined) return "null";
    if (typeof obj === "number" || typeof obj === "boolean") return String(obj);
    if (typeof obj === "string") return '"' + obj.replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/\n/g, "\\n").replace(/\r/g, "\\r") + '"';
    if (obj instanceof Array) {
        var items = [];
        for (var i = 0; i < obj.length; i++) items.push(jsonStringify(obj[i]));
        return "[" + items.join(",") + "]";
    }
    if (typeof obj === "object") {
        var pairs = [];
        for (var k in obj) {
            if (obj.hasOwnProperty(k)) pairs.push('"' + k + '":' + jsonStringify(obj[k]));
        }
        return "{" + pairs.join(",") + "}";
    }
    return String(obj);
}

function sanitizeName(name) {
    // Remove/replace chars unsafe for filenames; collapse multiple underscores
    var s = name.replace(/[^a-zA-Z0-9\-\.]/g, "_");
    s = s.replace(/_+/g, "_");
    s = s.replace(/^_+|_+$/g, "");
    return s || "layer";
}

function ensureFolder(path) {
    var f = new Folder(path);
    if (!f.exists) f.create();
}

// ── Categorization ────────────────────────────────────────────────────────────

function categorizeLayer(layerName, categories) {
    var lower = layerName.toLowerCase();
    // Priority order: logos > elementos > fundos
    var order = ["logos", "elementos", "fundos"];
    for (var i = 0; i < order.length; i++) {
        var cat = order[i];
        if (!categories[cat]) continue;
        var keywords = categories[cat];
        for (var k = 0; k < keywords.length; k++) {
            if (lower.indexOf(keywords[k].toLowerCase()) >= 0) {
                return cat;
            }
        }
    }
    return "outros";
}

// ── Export: Artboards ─────────────────────────────────────────────────────────

function exportArtboardSVG(doc, artboardIndex, outputPathNoExt) {
    doc.artboards.setActiveArtboardIndex(artboardIndex);
    var svgOpts = new ExportOptionsSVG();
    svgOpts.artBoardClipping = true;
    svgOpts.embedRasterImages = true;
    svgOpts.fontType = SVGFontType.OUTLINEFONT;
    svgOpts.coordinatePrecision = 3;
    svgOpts.documentEncoding = SVGDocumentEncoding.UTF8;
    // exportFile appends .svg automatically
    doc.exportFile(new File(outputPathNoExt), ExportType.SVG, svgOpts);
}

function exportArtboardPNG(doc, artboardIndex, outputPathNoExt, dpi) {
    doc.artboards.setActiveArtboardIndex(artboardIndex);
    var pngOpts = new ExportOptionsPNG24();
    pngOpts.artBoardClipping = true;
    pngOpts.resolution = dpi || 300;
    pngOpts.transparency = true;
    pngOpts.antiAliasing = true;
    // PNG24 does NOT auto-append .png — pass explicit extension
    doc.exportFile(new File(outputPathNoExt + ".png"), ExportType.PNG24, pngOpts);
}

// ── Export: Layers (hide-others pattern) ─────────────────────────────────────

function saveVisibility(doc) {
    var vis = [];
    for (var i = 0; i < doc.layers.length; i++) {
        vis.push(doc.layers[i].visible);
    }
    return vis;
}

function restoreVisibility(doc, vis) {
    for (var i = 0; i < doc.layers.length; i++) {
        try { doc.layers[i].visible = vis[i]; } catch (e) {}
    }
}

function exportLayerSVG(doc, layer, outputPathNoExt) {
    var vis = saveVisibility(doc);
    for (var i = 0; i < doc.layers.length; i++) {
        try { doc.layers[i].visible = false; } catch (e) {}
    }
    try { layer.visible = true; } catch (e) {}

    // Export full document bounds (no artboard clipping) to capture all layer content
    var svgOpts = new ExportOptionsSVG();
    svgOpts.artBoardClipping = false;
    svgOpts.embedRasterImages = true;
    svgOpts.fontType = SVGFontType.OUTLINEFONT;
    svgOpts.coordinatePrecision = 3;
    svgOpts.documentEncoding = SVGDocumentEncoding.UTF8;
    doc.exportFile(new File(outputPathNoExt), ExportType.SVG, svgOpts);

    restoreVisibility(doc, vis);
}

function exportLayerPNG(doc, layer, outputPathNoExt, dpi) {
    var vis = saveVisibility(doc);
    for (var i = 0; i < doc.layers.length; i++) {
        try { doc.layers[i].visible = false; } catch (e) {}
    }
    try { layer.visible = true; } catch (e) {}

    var pngOpts = new ExportOptionsPNG24();
    pngOpts.artBoardClipping = false;
    pngOpts.resolution = dpi || 300;
    pngOpts.transparency = true;
    pngOpts.antiAliasing = true;
    // PNG24 does NOT auto-append .png — pass explicit extension
    doc.exportFile(new File(outputPathNoExt + ".png"), ExportType.PNG24, pngOpts);

    restoreVisibility(doc, vis);
}

// ── Main ──────────────────────────────────────────────────────────────────────

function main() {
    var result = {
        status: "error",
        artboards: [],
        layers: [],
        errors: []
    };

    try {
        app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

        var config = readJSON(CONFIG_PATH);
        var doc = app.activeDocument;
        var outputDir = config.output_dir;
        var dpi = config.artboard_dpi || 300;
        var categories = config.categories || {
            logos: ["logo", "logotipo", "marca", "simbolo", "brand"],
            elementos: ["elemento", "detalhe", "grafismo", "icone", "icon", "pattern", "textura"],
            fundos: ["fundo", "background", "bg", "base"]
        };

        // Create output subdirectories
        ensureFolder(outputDir + "/paginas");
        ensureFolder(outputDir + "/logos");
        ensureFolder(outputDir + "/elementos");
        ensureFolder(outputDir + "/fundos");
        ensureFolder(outputDir + "/outros");

        // 1. Export each artboard as SVG + PNG
        for (var ai = 0; ai < doc.artboards.length; ai++) {
            var ab = doc.artboards[ai];
            var abLabel = ab.name ? sanitizeName(ab.name) : ("artboard_" + (ai + 1));
            // Pad index for natural sort: 01, 02...
            var pad = (ai + 1) < 10 ? "0" + (ai + 1) : "" + (ai + 1);
            var abBase = outputDir + "/paginas/" + pad + "_" + abLabel;

            var abEntry = {
                index: ai,
                name: ab.name,
                svg: "",
                png: "",
                errors: []
            };

            try {
                exportArtboardSVG(doc, ai, abBase);
                abEntry.svg = abBase + ".svg";
            } catch (e) {
                abEntry.errors.push("SVG: " + e.message);
                result.errors.push("Artboard " + ai + " SVG: " + e.message);
            }
            try {
                exportArtboardPNG(doc, ai, abBase, dpi);
                abEntry.png = abBase + ".png";
            } catch (e) {
                abEntry.errors.push("PNG: " + e.message);
                result.errors.push("Artboard " + ai + " PNG: " + e.message);
            }

            result.artboards.push(abEntry);
        }

        // 2. Categorize and export each layer individually
        for (var li = 0; li < doc.layers.length; li++) {
            var layer = doc.layers[li];

            // Skip empty layers
            if (layer.pageItems.length === 0) {
                result.layers.push({
                    name: layer.name,
                    category: "vazia",
                    items: 0,
                    svg: "",
                    png: "",
                    errors: []
                });
                continue;
            }

            var category = categorizeLayer(layer.name, categories);
            var layerLabel = sanitizeName(layer.name || ("layer_" + (li + 1)));
            var pad2 = (li + 1) < 10 ? "0" + (li + 1) : "" + (li + 1);
            var layerBase = outputDir + "/" + category + "/" + pad2 + "_" + layerLabel;

            var layerEntry = {
                name: layer.name,
                category: category,
                visible: layer.visible,
                items: layer.pageItems.length,
                svg: "",
                png: "",
                errors: []
            };

            try {
                exportLayerSVG(doc, layer, layerBase);
                layerEntry.svg = layerBase + ".svg";
            } catch (e) {
                layerEntry.errors.push("SVG: " + e.message);
                result.errors.push("Layer '" + layer.name + "' SVG: " + e.message);
            }
            try {
                exportLayerPNG(doc, layer, layerBase, dpi);
                layerEntry.png = layerBase + ".png";
            } catch (e) {
                layerEntry.errors.push("PNG: " + e.message);
                result.errors.push("Layer '" + layer.name + "' PNG: " + e.message);
            }

            result.layers.push(layerEntry);
        }

        result.status = result.errors.length > 0 ? "partial" : "success";

    } catch (err) {
        result.status = "error";
        result.errors.push(err.message);
    } finally {
        try { app.userInteractionLevel = UserInteractionLevel.DISPLAYALERTS; } catch (e) {}
    }

    var resultPath = CONFIG_PATH.replace(".json", "_result.json");
    writeJSON(resultPath, result);

    return jsonStringify({
        status: result.status,
        artboards: result.artboards.length,
        layers: result.layers.length,
        errors: result.errors.length
    });
}

main();
