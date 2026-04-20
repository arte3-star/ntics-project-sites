/**
 * read_document_colors.jsx — Le todas as cores usadas no documento ativo do Illustrator.
 *
 * Retorna JSON com:
 * - Cores CMYK unicas encontradas (fills e strokes)
 * - Cores de texto (character-level)
 * - Swatches do documento
 * - Informacoes do documento (nome, artboards, layers)
 *
 * Variavel RESULT_PATH e injetada pelo Python antes da execucao.
 */

// RESULT_PATH is injected by Python wrapper
// var RESULT_PATH = "C:/path/to/colors_result.json";

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

function writeJSON(filePath, obj) {
    var f = new File(filePath);
    f.open("w");
    f.encoding = "UTF-8";
    f.write(jsonStringify(obj));
    f.close();
}

function roundCMYK(c) {
    return [Math.round(c[0] * 100) / 100, Math.round(c[1] * 100) / 100, Math.round(c[2] * 100) / 100, Math.round(c[3] * 100) / 100];
}

function cmykKey(c) {
    return Math.round(c[0]) + "," + Math.round(c[1]) + "," + Math.round(c[2]) + "," + Math.round(c[3]);
}

function rgbKey(r, g, b) {
    return Math.round(r) + "," + Math.round(g) + "," + Math.round(b);
}

function rgbToHex(r, g, b) {
    function toHex(n) {
        var h = Math.round(n).toString(16).toUpperCase();
        return h.length < 2 ? "0" + h : h;
    }
    return "#" + toHex(r) + toHex(g) + toHex(b);
}

// -- Color extraction ---------------------------------------------------------

var colorMap = {};  // key -> {cmyk, rgb, hex, count, usage}

function addColor(color, usage) {
    if (!color) return;

    var cmyk = null;
    var rgb = null;
    var hex = "";
    var key = "";

    try {
        if (color.typename === "CMYKColor") {
            cmyk = [color.cyan, color.magenta, color.yellow, color.black];
            key = "cmyk:" + cmykKey(cmyk);
        } else if (color.typename === "RGBColor") {
            rgb = [color.red, color.green, color.blue];
            hex = rgbToHex(color.red, color.green, color.blue);
            key = "rgb:" + rgbKey(color.red, color.green, color.blue);
        } else if (color.typename === "SpotColor") {
            var spot = color.spot.color;
            if (spot.typename === "CMYKColor") {
                cmyk = [spot.cyan, spot.magenta, spot.yellow, spot.black];
                key = "spot-cmyk:" + cmykKey(cmyk) + ":" + color.spot.name;
            } else if (spot.typename === "RGBColor") {
                rgb = [spot.red, spot.green, spot.blue];
                hex = rgbToHex(spot.red, spot.green, spot.blue);
                key = "spot-rgb:" + rgbKey(spot.red, spot.green, spot.blue) + ":" + color.spot.name;
            }
        } else if (color.typename === "GrayColor") {
            key = "gray:" + Math.round(color.gray);
        } else if (color.typename === "NoColor") {
            return; // skip
        } else {
            return; // skip unknown
        }
    } catch (e) {
        return;
    }

    if (!key) return;

    if (colorMap[key]) {
        colorMap[key].count++;
        if (colorMap[key].usage.indexOf(usage) < 0) {
            colorMap[key].usage += ", " + usage;
        }
    } else {
        colorMap[key] = {
            cmyk: cmyk ? roundCMYK(cmyk) : null,
            rgb: rgb,
            hex: hex,
            gray: color.typename === "GrayColor" ? Math.round(color.gray) : null,
            spot_name: (color.typename === "SpotColor") ? color.spot.name : null,
            count: 1,
            usage: usage
        };
    }
}

function processItem(item, layerName) {
    try {
        if (item.fillColor) addColor(item.fillColor, "fill@" + layerName);
    } catch (e) {}
    try {
        if (item.strokeColor) addColor(item.strokeColor, "stroke@" + layerName);
    } catch (e) {}

    // Gradient stops
    try {
        if (item.fillColor && item.fillColor.typename === "GradientColor") {
            var stops = item.fillColor.gradient.gradientStops;
            for (var s = 0; s < stops.length; s++) {
                addColor(stops[s].color, "gradient-fill@" + layerName);
            }
        }
    } catch (e) {}
    try {
        if (item.strokeColor && item.strokeColor.typename === "GradientColor") {
            var stops2 = item.strokeColor.gradient.gradientStops;
            for (var s2 = 0; s2 < stops2.length; s2++) {
                addColor(stops2[s2].color, "gradient-stroke@" + layerName);
            }
        }
    } catch (e) {}
}

function processTextFrame(tf, layerName) {
    // Frame-level color
    processItem(tf, layerName);

    // Character-level colors
    try {
        var chars = tf.textRange.characters;
        var lastKey = "";
        for (var c = 0; c < chars.length; c++) {
            try {
                var charAttr = chars[c].characterAttributes;
                if (charAttr.fillColor) {
                    addColor(charAttr.fillColor, "text@" + layerName);
                }
            } catch (e) {}
        }
    } catch (e) {}
}

function processGroup(group, layerName) {
    for (var i = 0; i < group.pathItems.length; i++) {
        processItem(group.pathItems[i], layerName);
    }
    for (var j = 0; j < group.compoundPathItems.length; j++) {
        processItem(group.compoundPathItems[j], layerName);
    }
    for (var t = 0; t < group.textFrames.length; t++) {
        processTextFrame(group.textFrames[t], layerName);
    }
    // Recurse into sub-groups
    for (var g = 0; g < group.groupItems.length; g++) {
        processGroup(group.groupItems[g], layerName);
    }
}

function processLayer(layer) {
    var name = layer.name;

    for (var i = 0; i < layer.pathItems.length; i++) {
        processItem(layer.pathItems[i], name);
    }
    for (var j = 0; j < layer.compoundPathItems.length; j++) {
        processItem(layer.compoundPathItems[j], name);
    }
    for (var t = 0; t < layer.textFrames.length; t++) {
        processTextFrame(layer.textFrames[t], name);
    }
    for (var g = 0; g < layer.groupItems.length; g++) {
        processGroup(layer.groupItems[g], name);
    }
    // Recurse sublayers
    for (var s = 0; s < layer.layers.length; s++) {
        processLayer(layer.layers[s]);
    }
}

// -- Main ---------------------------------------------------------------------

function main() {
    var result = {
        status: "error",
        document: {},
        colors: [],
        swatches: [],
        layers: [],
        text_frames: [],
        errors: []
    };

    try {
        var doc = app.activeDocument;

        // Document info
        result.document = {
            name: doc.name,
            path: doc.path ? doc.path.fsName : "",
            color_space: doc.documentColorSpace == DocumentColorSpace.CMYK ? "CMYK" : "RGB",
            artboards: doc.artboards.length,
            layers: doc.layers.length,
            width_mm: Math.round(doc.width / 2.83465 * 10) / 10,
            height_mm: Math.round(doc.height / 2.83465 * 10) / 10
        };

        // Layers info
        for (var l = 0; l < doc.layers.length; l++) {
            var layer = doc.layers[l];
            result.layers.push({
                name: layer.name,
                visible: layer.visible,
                locked: layer.locked,
                items: layer.pageItems.length
            });
        }

        // Text frames summary
        for (var tf = 0; tf < doc.textFrames.length; tf++) {
            var frame = doc.textFrames[tf];
            result.text_frames.push({
                name: frame.name || ("TextFrame_" + tf),
                contents: frame.contents.substring(0, 100),
                layer: frame.layer.name
            });
        }

        // Swatches
        for (var sw = 0; sw < doc.swatches.length; sw++) {
            var swatch = doc.swatches[sw];
            try {
                var swColor = swatch.color;
                var swInfo = {
                    name: swatch.name,
                    type: swColor.typename
                };
                if (swColor.typename === "CMYKColor") {
                    swInfo.cmyk = roundCMYK([swColor.cyan, swColor.magenta, swColor.yellow, swColor.black]);
                } else if (swColor.typename === "RGBColor") {
                    swInfo.rgb = [Math.round(swColor.red), Math.round(swColor.green), Math.round(swColor.blue)];
                    swInfo.hex = rgbToHex(swColor.red, swColor.green, swColor.blue);
                } else if (swColor.typename === "SpotColor") {
                    var spotC = swColor.spot.color;
                    if (spotC.typename === "CMYKColor") {
                        swInfo.cmyk = roundCMYK([spotC.cyan, spotC.magenta, spotC.yellow, spotC.black]);
                    }
                    swInfo.spot_name = swColor.spot.name;
                }
                // Skip [None] and [Registration]
                if (swatch.name !== "[None]" && swatch.name !== "[Registration]") {
                    result.swatches.push(swInfo);
                }
            } catch (e) {}
        }

        // Process all layers for colors
        for (var pl = 0; pl < doc.layers.length; pl++) {
            processLayer(doc.layers[pl]);
        }

        // Convert colorMap to array, sorted by count
        var colorArray = [];
        for (var key in colorMap) {
            if (colorMap.hasOwnProperty(key)) {
                colorArray.push(colorMap[key]);
            }
        }
        colorArray.sort(function(a, b) { return b.count - a.count; });
        result.colors = colorArray;

        result.status = "success";

    } catch (err) {
        result.errors.push(err.message);
    }

    writeJSON(RESULT_PATH, result);
    return jsonStringify({status: result.status, total_colors: result.colors.length});
}

main();
