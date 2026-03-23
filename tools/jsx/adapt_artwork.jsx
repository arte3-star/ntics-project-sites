/**
 * adapt_artwork.jsx — Adapta arte com identidade visual do cliente no Illustrator.
 *
 * Executado via COM (app.DoJavaScript) pelo wrapper Python.
 * Lê config JSON com: color_map, logo, fonts, export settings.
 * Grava resultado em _result.json ao finalizar.
 *
 * Variável CONFIG_PATH é injetada pelo Python antes da execução.
 */

// CONFIG_PATH is injected by Python wrapper before execution
// var CONFIG_PATH = "C:/path/to/adapt_config.json";

// ── Helpers ──────────────────────────────────────────────────────────────────

function readJSON(filePath) {
    var f = new File(filePath);
    if (!f.exists) throw new Error("Config file not found: " + filePath);
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
    if (typeof obj === "string") return '"' + obj.replace(/\\/g, "\\\\").replace(/"/g, '\\"') + '"';
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

function makeCMYK(arr) {
    var c = new CMYKColor();
    c.cyan = arr[0];
    c.magenta = arr[1];
    c.yellow = arr[2];
    c.black = arr[3];
    return c;
}

function cmykMatch(color, target, tolerance) {
    if (color.typename !== "CMYKColor") return false;
    return (
        Math.abs(color.cyan - target[0]) <= tolerance &&
        Math.abs(color.magenta - target[1]) <= tolerance &&
        Math.abs(color.yellow - target[2]) <= tolerance &&
        Math.abs(color.black - target[3]) <= tolerance
    );
}

function rgbToCmyk(r, g, b) {
    var c = 1 - (r / 255);
    var m = 1 - (g / 255);
    var y = 1 - (b / 255);
    var k = Math.min(c, m, y);
    if (k === 1) return [0, 0, 0, 100];
    return [
        Math.round(((c - k) / (1 - k)) * 100),
        Math.round(((m - k) / (1 - k)) * 100),
        Math.round(((y - k) / (1 - k)) * 100),
        Math.round(k * 100)
    ];
}

// ── Color Replacement ────────────────────────────────────────────────────────

var colorsReplaced = 0;

function replaceColorIfMatch(item, colorMap, tolerance) {
    for (var i = 0; i < colorMap.length; i++) {
        var fromC = colorMap[i].from_cmyk;
        var toC = colorMap[i].to_cmyk;
        var newColor = makeCMYK(toC);

        // Fill color
        try {
            if (item.fillColor && item.fillColor.typename === "CMYKColor") {
                if (cmykMatch(item.fillColor, fromC, tolerance)) {
                    item.fillColor = newColor;
                    colorsReplaced++;
                }
            }
            // Handle spot colors by checking underlying CMYK
            if (item.fillColor && item.fillColor.typename === "SpotColor") {
                var spot = item.fillColor.spot.color;
                if (spot.typename === "CMYKColor" && cmykMatch(spot, fromC, tolerance)) {
                    item.fillColor = newColor;
                    colorsReplaced++;
                }
            }
        } catch (e) { /* some items don't support fillColor */ }

        // Stroke color
        try {
            if (item.strokeColor && item.strokeColor.typename === "CMYKColor") {
                if (cmykMatch(item.strokeColor, fromC, tolerance)) {
                    item.strokeColor = newColor;
                    colorsReplaced++;
                }
            }
            if (item.strokeColor && item.strokeColor.typename === "SpotColor") {
                var spotS = item.strokeColor.spot.color;
                if (spotS.typename === "CMYKColor" && cmykMatch(spotS, fromC, tolerance)) {
                    item.strokeColor = newColor;
                    colorsReplaced++;
                }
            }
        } catch (e) { /* some items don't support strokeColor */ }
    }
}

function replaceGradientColors(item, colorMap, tolerance) {
    try {
        if (item.fillColor && item.fillColor.typename === "GradientColor") {
            var stops = item.fillColor.gradient.gradientStops;
            for (var s = 0; s < stops.length; s++) {
                var stopColor = stops[s].color;
                if (stopColor.typename === "CMYKColor") {
                    for (var i = 0; i < colorMap.length; i++) {
                        if (cmykMatch(stopColor, colorMap[i].from_cmyk, tolerance)) {
                            stops[s].color = makeCMYK(colorMap[i].to_cmyk);
                            colorsReplaced++;
                        }
                    }
                }
            }
        }
    } catch (e) { /* gradient access may fail on some items */ }
}

function processTextFrameColors(textFrame, colorMap, tolerance) {
    try {
        for (var c = 0; c < textFrame.textRange.characters.length; c++) {
            var charAttr = textFrame.textRange.characters[c].characterAttributes;
            if (charAttr.fillColor && charAttr.fillColor.typename === "CMYKColor") {
                for (var i = 0; i < colorMap.length; i++) {
                    if (cmykMatch(charAttr.fillColor, colorMap[i].from_cmyk, colorMap[i].tolerance || tolerance)) {
                        charAttr.fillColor = makeCMYK(colorMap[i].to_cmyk);
                        colorsReplaced++;
                    }
                }
            }
        }
    } catch (e) { /* character-level color may not be accessible */ }
}

function processItems(items, colorMap, tolerance) {
    for (var i = 0; i < items.length; i++) {
        var item = items[i];
        replaceColorIfMatch(item, colorMap, tolerance);
        replaceGradientColors(item, colorMap, tolerance);
    }
}

function processLayer(layer, colorMap, tolerance) {
    processItems(layer.pathItems, colorMap, tolerance);
    processItems(layer.compoundPathItems, colorMap, tolerance);

    // Text frames — item-level + character-level
    for (var t = 0; t < layer.textFrames.length; t++) {
        replaceColorIfMatch(layer.textFrames[t], colorMap, tolerance);
        processTextFrameColors(layer.textFrames[t], colorMap, tolerance);
    }

    // Recurse into groups
    for (var g = 0; g < layer.groupItems.length; g++) {
        processItems(layer.groupItems[g].pathItems, colorMap, tolerance);
        processItems(layer.groupItems[g].compoundPathItems, colorMap, tolerance);
        for (var t2 = 0; t2 < layer.groupItems[g].textFrames.length; t2++) {
            replaceColorIfMatch(layer.groupItems[g].textFrames[t2], colorMap, tolerance);
            processTextFrameColors(layer.groupItems[g].textFrames[t2], colorMap, tolerance);
        }
    }

    // Recurse into sublayers
    for (var s = 0; s < layer.layers.length; s++) {
        processLayer(layer.layers[s], colorMap, tolerance);
    }
}

// ── Logo Placement ───────────────────────────────────────────────────────────

var logoPlaced = false;

function placeLogo(doc, logoConfig) {
    if (!logoConfig || !logoConfig.file) return;

    var logoFile = new File(logoConfig.file);
    if (!logoFile.exists) throw new Error("Logo file not found: " + logoConfig.file);

    // Find or create target layer
    var targetLayer;
    try {
        targetLayer = doc.layers.getByName(logoConfig.target_layer || "Logo");
        // Clear existing items in the logo layer
        while (targetLayer.pageItems.length > 0) {
            targetLayer.pageItems[0].remove();
        }
    } catch (e) {
        targetLayer = doc.layers.add();
        targetLayer.name = logoConfig.target_layer || "Logo_Cliente";
    }

    // Place the logo
    var placed = doc.placedItems.add();
    placed.file = logoFile;
    placed.embed();
    // Move to target layer
    placed.move(targetLayer, ElementPlacement.PLACEATBEGINNING);

    // Scale to max width (mm → points: 1mm = 2.83465pt)
    if (logoConfig.max_width_mm) {
        var maxWidthPt = logoConfig.max_width_mm * 2.83465;
        var currentWidth = placed.width;
        if (currentWidth > maxWidthPt) {
            var scaleFactor = (maxWidthPt / currentWidth) * 100;
            placed.resize(scaleFactor, scaleFactor);
        }
    }

    // Position on artboard
    var ab = doc.artboards[doc.artboards.getActiveArtboardIndex()];
    var abRect = ab.artboardRect; // [left, top, right, bottom]
    var margin = 10 * 2.83465; // 10mm margin in points

    var pos = logoConfig.position || "top-right";
    switch (pos) {
        case "top-left":
            placed.left = abRect[0] + margin;
            placed.top = abRect[1] - margin;
            break;
        case "top-right":
            placed.left = abRect[2] - placed.width - margin;
            placed.top = abRect[1] - margin;
            break;
        case "bottom-left":
            placed.left = abRect[0] + margin;
            placed.top = abRect[3] + placed.height + margin;
            break;
        case "bottom-right":
            placed.left = abRect[2] - placed.width - margin;
            placed.top = abRect[3] + placed.height + margin;
            break;
        case "center":
            placed.left = (abRect[0] + abRect[2]) / 2 - placed.width / 2;
            placed.top = (abRect[1] + abRect[3]) / 2 + placed.height / 2;
            break;
        default:
            placed.left = abRect[2] - placed.width - margin;
            placed.top = abRect[1] - margin;
    }

    logoPlaced = true;
}

// ── Font Substitution ────────────────────────────────────────────────────────

var fontsChanged = 0;

function substituteFonts(doc, fontMap) {
    if (!fontMap || fontMap.length === 0) return;

    for (var t = 0; t < doc.textFrames.length; t++) {
        var tf = doc.textFrames[t];
        for (var c = 0; c < tf.textRange.characters.length; c++) {
            var charAttr = tf.textRange.characters[c].characterAttributes;
            try {
                var currentFontName = charAttr.textFont.name;
                for (var f = 0; f < fontMap.length; f++) {
                    if (currentFontName === fontMap[f].from) {
                        charAttr.textFont = app.textFonts.getByName(fontMap[f].to);
                        fontsChanged++;
                    }
                }
            } catch (e) {
                // Font not installed or not accessible — skip
            }
        }
    }
}

// ── Export Functions ──────────────────────────────────────────────────────────

function exportPDF(doc, outputPath, exportConfig) {
    var bleedPt = (exportConfig.bleed_mm || 3) * 2.83465;

    var pdfOpts = new PDFSaveOptions();
    // Try to use the specified preset, fall back to default
    try {
        pdfOpts.pDFPreset = "[" + (exportConfig.pdf_preset || "PDF/X-4:2008") + "]";
    } catch (e) {
        // Preset not found, use manual settings
    }
    pdfOpts.compatibility = PDFCompatibility.ACROBAT7;
    pdfOpts.preserveEditability = false;
    pdfOpts.generateThumbnails = true;
    pdfOpts.colorBars = true;
    pdfOpts.trimMarks = true;
    pdfOpts.registrationMarks = true;
    pdfOpts.bleedOffsetRect = [bleedPt, bleedPt, bleedPt, bleedPt];
    pdfOpts.colorCompression = CompressionQuality.AUTOMATICJPEGHIGH;

    var pdfFile = new File(outputPath);
    doc.saveAs(pdfFile, pdfOpts);
    return outputPath;
}

function exportSVG(doc, outputPath) {
    var svgOpts = new ExportOptionsSVG();
    svgOpts.embedRasterImages = true;
    svgOpts.fontType = SVGFontType.OUTLINEFONT;
    svgOpts.coordinatePrecision = 3;
    svgOpts.documentEncoding = SVGDocumentEncoding.UTF8;

    var svgFile = new File(outputPath);
    doc.exportFile(svgFile, ExportType.SVG, svgOpts);
    return outputPath;
}

// ── Main ─────────────────────────────────────────────────────────────────────

function main() {
    var result = {
        status: "error",
        colors_replaced: 0,
        logo_placed: false,
        fonts_changed: 0,
        exports: [],
        errors: []
    };

    try {
        // Suppress dialogs
        app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

        // Read config
        var config = readJSON(CONFIG_PATH);
        var doc = app.activeDocument;
        var tolerance = config.color_tolerance || 5;

        // 1. Replace colors
        if (config.color_map && config.color_map.length > 0) {
            for (var l = 0; l < doc.layers.length; l++) {
                processLayer(doc.layers[l], config.color_map, tolerance);
            }
        }

        // 2. Place logo
        try {
            placeLogo(doc, config.logo);
        } catch (logoErr) {
            result.errors.push("Logo: " + logoErr.message);
        }

        // 3. Substitute fonts
        try {
            substituteFonts(doc, config.fonts);
        } catch (fontErr) {
            result.errors.push("Fonts: " + fontErr.message);
        }

        // 4. Export
        var outputDir = config.output_dir || Folder.desktop.fsName;
        var baseName = config.client_name ? config.client_name.replace(/[^a-zA-Z0-9_-]/g, "_") : "adapted";

        if (!config.export || config.export.pdf !== false) {
            var pdfPath = outputDir + "/" + baseName + ".pdf";
            try {
                exportPDF(doc, pdfPath, config.export || {});
                result.exports.push(pdfPath);
            } catch (pdfErr) {
                result.errors.push("PDF export: " + pdfErr.message);
            }
        }

        if (config.export && config.export.svg) {
            var svgPath = outputDir + "/" + baseName + ".svg";
            try {
                exportSVG(doc, svgPath);
                result.exports.push(svgPath);
            } catch (svgErr) {
                result.errors.push("SVG export: " + svgErr.message);
            }
        }

        // Set result
        result.status = result.errors.length > 0 ? "partial" : "success";
        result.colors_replaced = colorsReplaced;
        result.logo_placed = logoPlaced;
        result.fonts_changed = fontsChanged;

    } catch (err) {
        result.status = "error";
        result.errors.push(err.message);
    } finally {
        // Restore interaction level
        try { app.userInteractionLevel = UserInteractionLevel.DISPLAYALERTS; } catch (e) {}
    }

    // Write result JSON
    var resultPath = CONFIG_PATH.replace(".json", "_result.json");
    writeJSON(resultPath, result);

    return jsonStringify(result);
}

main();
