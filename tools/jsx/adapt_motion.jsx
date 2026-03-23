/**
 * adapt_motion.jsx — Adapta template de motion graphics com dados do cliente no After Effects.
 *
 * Executado via COM (app.DoJavaScript) ou via AfterFX.exe -r pelo wrapper Python.
 * Lê config JSON com: text_map, footage_map, color_map, render settings.
 * Grava resultado em _result.json ao finalizar.
 *
 * Variável CONFIG_PATH é injetada pelo Python wrapper antes da execução.
 */

// CONFIG_PATH is injected by Python wrapper before execution
// var CONFIG_PATH = "C:/path/to/motion_config.json";

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
    if (typeof obj === "string") return '"' + obj.replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/\n/g, "\\n") + '"';
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

// ── Text Replacement ─────────────────────────────────────────────────────────

var textsReplaced = 0;

function replaceTextsInComp(comp, textMap) {
    if (!textMap || textMap.length === 0) return;

    for (var i = 1; i <= comp.numLayers; i++) {
        var layer = comp.layer(i);

        // Check if it's a text layer
        if (!(layer instanceof TextLayer)) continue;

        var sourceText = layer.property("Source Text");
        if (sourceText === null) continue;

        // Check by layer name match
        for (var t = 0; t < textMap.length; t++) {
            var entry = textMap[t];

            // Match by layer name
            if (entry.layer_name && layer.name === entry.layer_name) {
                if (sourceText.numKeys === 0) {
                    var textDoc = sourceText.value;
                    textDoc.text = entry.new_text;
                    // Optionally set font
                    if (entry.font) {
                        textDoc.font = entry.font;
                    }
                    if (entry.font_size) {
                        textDoc.fontSize = entry.font_size;
                    }
                    if (entry.color) {
                        textDoc.fillColor = entry.color; // [R, G, B] normalized 0-1
                    }
                    sourceText.setValue(textDoc);
                    textsReplaced++;
                } else {
                    // Replace in all keyframes
                    for (var k = 1; k <= sourceText.numKeys; k++) {
                        var kTextDoc = sourceText.keyValue(k);
                        kTextDoc.text = entry.new_text;
                        if (entry.font) kTextDoc.font = entry.font;
                        if (entry.font_size) kTextDoc.fontSize = entry.font_size;
                        if (entry.color) kTextDoc.fillColor = entry.color;
                        sourceText.setValueAtKey(k, kTextDoc);
                        textsReplaced++;
                    }
                }
                break;
            }

            // Match by find/replace in text content
            if (entry.find && !entry.layer_name) {
                if (sourceText.numKeys === 0) {
                    var textDoc2 = sourceText.value;
                    if (textDoc2.text.indexOf(entry.find) !== -1) {
                        var re = new RegExp(entry.find.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "g");
                        textDoc2.text = textDoc2.text.replace(re, entry.replace || entry.new_text || "");
                        sourceText.setValue(textDoc2);
                        textsReplaced++;
                    }
                } else {
                    for (var k2 = 1; k2 <= sourceText.numKeys; k2++) {
                        var kDoc = sourceText.keyValue(k2);
                        if (kDoc.text.indexOf(entry.find) !== -1) {
                            var re2 = new RegExp(entry.find.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "g");
                            kDoc.text = kDoc.text.replace(re2, entry.replace || entry.new_text || "");
                            sourceText.setValueAtKey(k2, kDoc);
                            textsReplaced++;
                        }
                    }
                }
            }
        }
    }
}

// ── Footage Replacement ──────────────────────────────────────────────────────

var footageReplaced = 0;

function replaceFootageInProject(project, footageMap) {
    if (!footageMap || footageMap.length === 0) return;

    for (var f = 0; f < footageMap.length; f++) {
        var entry = footageMap[f];
        var newFile = new File(entry.new_file);

        if (!newFile.exists) {
            throw new Error("Footage file not found: " + entry.new_file);
        }

        // Find the footage item by name in the project
        var found = false;
        for (var i = 1; i <= project.numItems; i++) {
            var item = project.item(i);

            // Match by item name or by layer_name
            var matchByName = (entry.item_name && item.name === entry.item_name);
            var matchByFile = (entry.original_file && item instanceof FootageItem &&
                              item.file && item.file.name === new File(entry.original_file).name);

            if (matchByName || matchByFile) {
                if (item instanceof FootageItem) {
                    item.replace(newFile);
                    footageReplaced++;
                    found = true;
                    // Don't break — there might be multiple items with same name
                }
            }
        }

        // Alternative: find layer by name in the target comp and replace its source
        if (!found && entry.layer_name) {
            // Will be handled at comp level
        }
    }
}

function replaceFootageInComp(comp, footageMap) {
    if (!footageMap || footageMap.length === 0) return;

    for (var i = 1; i <= comp.numLayers; i++) {
        var layer = comp.layer(i);

        for (var f = 0; f < footageMap.length; f++) {
            var entry = footageMap[f];
            if (entry.layer_name && layer.name === entry.layer_name) {
                var newFile = new File(entry.new_file);
                if (!newFile.exists) continue;

                if (layer.source instanceof FootageItem) {
                    layer.source.replace(newFile);
                    footageReplaced++;
                }
            }
        }
    }
}

// ── Color Replacement (Shape Layers & Solids) ────────────────────────────────

var colorsReplaced = 0;

function normalizeColor(arr) {
    // Accept both 0-255 and 0-1 ranges; return 0-1
    if (arr[0] > 1 || arr[1] > 1 || arr[2] > 1) {
        return [arr[0] / 255, arr[1] / 255, arr[2] / 255];
    }
    return arr;
}

function colorsClose(a, b, tolerance) {
    var tol = tolerance || 0.05; // 0-1 range tolerance
    return (
        Math.abs(a[0] - b[0]) <= tol &&
        Math.abs(a[1] - b[1]) <= tol &&
        Math.abs(a[2] - b[2]) <= tol
    );
}

function replaceColorsInComp(comp, colorMap, tolerance) {
    if (!colorMap || colorMap.length === 0) return;

    for (var i = 1; i <= comp.numLayers; i++) {
        var layer = comp.layer(i);

        // Solid layers — check and replace color
        try {
            if (layer.source instanceof FootageItem && layer.source.mainSource instanceof SolidSource) {
                var solidColor = layer.source.mainSource.color;
                for (var c = 0; c < colorMap.length; c++) {
                    var fromC = normalizeColor(colorMap[c].from_rgb);
                    var toC = normalizeColor(colorMap[c].to_rgb);
                    if (colorsClose(solidColor, fromC, tolerance)) {
                        layer.source.mainSource.color = toC;
                        colorsReplaced++;
                    }
                }
            }
        } catch (e) { /* not a solid */ }

        // Shape layers — iterate shape groups for fill/stroke
        try {
            if (layer.matchName === "ADBE Vector Layer" || layer.property("Contents") !== null) {
                replaceColorsInShapeGroup(layer.property("Contents"), colorMap, tolerance);
            }
        } catch (e) { /* not a shape layer */ }

        // Text layers — fill color
        try {
            if (layer instanceof TextLayer) {
                var srcText = layer.property("Source Text");
                if (srcText !== null && srcText.numKeys === 0) {
                    var td = srcText.value;
                    var fc = td.fillColor;
                    for (var c2 = 0; c2 < colorMap.length; c2++) {
                        var fromC2 = normalizeColor(colorMap[c2].from_rgb);
                        var toC2 = normalizeColor(colorMap[c2].to_rgb);
                        if (colorsClose(fc, fromC2, tolerance)) {
                            td.fillColor = toC2;
                            srcText.setValue(td);
                            colorsReplaced++;
                        }
                    }
                }
            }
        } catch (e) { /* text color access failed */ }
    }
}

function replaceColorsInShapeGroup(group, colorMap, tolerance) {
    if (!group) return;

    for (var i = 1; i <= group.numProperties; i++) {
        var prop = group.property(i);

        // Fill color
        if (prop.matchName === "ADBE Vector Graphic - Fill") {
            try {
                var fillColor = prop.property("Color").value;
                for (var c = 0; c < colorMap.length; c++) {
                    var fromC = normalizeColor(colorMap[c].from_rgb);
                    var toC = normalizeColor(colorMap[c].to_rgb);
                    if (colorsClose(fillColor, fromC, tolerance)) {
                        prop.property("Color").setValue(toC);
                        colorsReplaced++;
                    }
                }
            } catch (e) {}
        }

        // Stroke color
        if (prop.matchName === "ADBE Vector Graphic - Stroke") {
            try {
                var strokeColor = prop.property("Color").value;
                for (var c3 = 0; c3 < colorMap.length; c3++) {
                    var fromC3 = normalizeColor(colorMap[c3].from_rgb);
                    var toC3 = normalizeColor(colorMap[c3].to_rgb);
                    if (colorsClose(strokeColor, fromC3, tolerance)) {
                        prop.property("Color").setValue(toC3);
                        colorsReplaced++;
                    }
                }
            } catch (e) {}
        }

        // Recurse into shape groups
        if (prop.matchName === "ADBE Vector Group" || prop.propertyType === PropertyType.INDEXED_GROUP) {
            try {
                var contents = prop.property("Contents");
                if (contents) replaceColorsInShapeGroup(contents, colorMap, tolerance);
            } catch (e) {}
        }
    }
}

// ── Render Queue Setup ───────────────────────────────────────────────────────

function setupRender(comp, renderConfig) {
    if (!renderConfig) return null;

    var rqItem = app.project.renderQueue.items.add(comp);

    // Set output path
    if (renderConfig.output_path) {
        var om = rqItem.outputModule(1);
        om.file = new File(renderConfig.output_path);
    }

    // Set output module template
    if (renderConfig.output_template) {
        try {
            var om2 = rqItem.outputModule(1);
            om2.applyTemplate(renderConfig.output_template);
            // Re-set file after template (template may change extension)
            if (renderConfig.output_path) {
                om2.file = new File(renderConfig.output_path);
            }
        } catch (e) {
            // Template not found — use default
        }
    }

    // Set render settings template
    if (renderConfig.render_template) {
        try {
            rqItem.applyTemplate(renderConfig.render_template);
        } catch (e) {
            // Template not found — use default
        }
    }

    return rqItem;
}

// ── Main ─────────────────────────────────────────────────────────────────────

function main() {
    var result = {
        status: "error",
        texts_replaced: 0,
        footage_replaced: 0,
        colors_replaced: 0,
        render_queued: false,
        comp_name: "",
        errors: []
    };

    try {
        app.beginSuppressDialogs();

        // Read config
        var config = readJSON(CONFIG_PATH);
        var project = app.project;

        // Find target composition
        var comp = null;
        if (config.comp_name) {
            for (var i = 1; i <= project.numItems; i++) {
                if (project.item(i) instanceof CompItem && project.item(i).name === config.comp_name) {
                    comp = project.item(i);
                    break;
                }
            }
        }

        // If no comp specified or not found, use the first comp or active item
        if (!comp) {
            if (project.activeItem && project.activeItem instanceof CompItem) {
                comp = project.activeItem;
            } else {
                for (var j = 1; j <= project.numItems; j++) {
                    if (project.item(j) instanceof CompItem) {
                        comp = project.item(j);
                        break;
                    }
                }
            }
        }

        if (!comp) throw new Error("No composition found in project.");
        result.comp_name = comp.name;

        app.beginUndoGroup("Adapt Motion");

        // 1. Replace texts
        try {
            replaceTextsInComp(comp, config.text_map);
        } catch (textErr) {
            result.errors.push("Text: " + textErr.message);
        }

        // 2. Replace footage (project level + comp level)
        try {
            replaceFootageInProject(project, config.footage_map);
            replaceFootageInComp(comp, config.footage_map);
        } catch (footageErr) {
            result.errors.push("Footage: " + footageErr.message);
        }

        // 3. Replace colors
        try {
            var colorTolerance = config.color_tolerance || 0.05;
            replaceColorsInComp(comp, config.color_map, colorTolerance);
        } catch (colorErr) {
            result.errors.push("Colors: " + colorErr.message);
        }

        // 4. Setup render queue (if render config provided)
        if (config.render) {
            try {
                setupRender(comp, config.render);
                result.render_queued = true;
            } catch (renderErr) {
                result.errors.push("Render: " + renderErr.message);
            }
        }

        app.endUndoGroup();

        // 5. Save project if requested
        if (config.save_as) {
            try {
                project.save(new File(config.save_as));
            } catch (saveErr) {
                result.errors.push("Save: " + saveErr.message);
            }
        }

        // Set result
        result.status = result.errors.length > 0 ? "partial" : "success";
        result.texts_replaced = textsReplaced;
        result.footage_replaced = footageReplaced;
        result.colors_replaced = colorsReplaced;

    } catch (err) {
        result.status = "error";
        result.errors.push(err.message);
    } finally {
        try { app.endSuppressDialogs(false); } catch (e) {}
    }

    // Write result JSON
    var resultPath = CONFIG_PATH.replace(".json", "_result.json");
    writeJSON(resultPath, result);

    return jsonStringify(result);
}

main();
