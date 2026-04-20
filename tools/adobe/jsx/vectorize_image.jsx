/**
 * vectorize_image.jsx — Vetoriza imagens raster via Image Trace no Illustrator.
 *
 * Executado via COM (app.DoJavaScript) pelo wrapper Python.
 * Lê config JSON com: input files, preset, export formats.
 * Grava resultado em _result.json ao finalizar.
 *
 * Variável CONFIG_PATH é injetada pelo Python wrapper antes da execução.
 */

// CONFIG_PATH is injected by Python wrapper before execution
// var CONFIG_PATH = "C:/path/to/vectorize_config.json";

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

// ── Tracing Presets ──────────────────────────────────────────────────────────
//
// Illustrator has built-in tracing presets accessible via app.tracingPresetsList.
// Common presets (index may vary by locale/version):
//   [Default]
//   High Fidelity Photo
//   Low Fidelity Photo
//   3 Colors / 6 Colors / 16 Colors
//   Shades of Gray
//   Black and White Logo
//   Sketched Art
//   Silhouettes
//   Line Art
//   Technical Drawing
//
// We match by name substring for robustness across locales.

function findPresetIndex(presetName) {
    var presets = app.tracingPresetsList;
    // Exact match first
    for (var i = 0; i < presets.length; i++) {
        if (presets[i] === presetName) return i;
    }
    // Substring match (case-insensitive)
    var lower = presetName.toLowerCase();
    for (var j = 0; j < presets.length; j++) {
        if (presets[j].toLowerCase().indexOf(lower) !== -1) return j;
    }
    return -1;
}

// ── Vectorize Single Image ───────────────────────────────────────────────────

function vectorizeImage(imagePath, outputDir, baseName, config) {
    var imageFile = new File(imagePath);
    if (!imageFile.exists) throw new Error("Image not found: " + imagePath);

    var exports = [];

    // Create a new document
    var doc = app.documents.add(
        config.color_space === "CMYK" ? DocumentColorSpace.CMYK : DocumentColorSpace.RGB
    );

    // Place the raster image
    var placed = doc.placedItems.add();
    placed.file = imageFile;

    // Trace the image
    var traceObj = placed.trace();

    // Apply preset
    var presetName = config.preset || "High Fidelity Photo";
    var presetIdx = findPresetIndex(presetName);
    if (presetIdx >= 0) {
        traceObj.tracing.tracingOptions.loadFromPreset(app.tracingPresetsList[presetIdx]);
    }

    // Custom tracing options (override preset if provided)
    var opts = traceObj.tracing.tracingOptions;
    if (config.tracing_options) {
        var to = config.tracing_options;
        if (to.threshold !== undefined) opts.threshold = to.threshold;
        if (to.corners !== undefined) opts.cornerAngle = to.corners;
        if (to.paths !== undefined) opts.pathFitting = to.paths;
        if (to.noise !== undefined) opts.noiseFidelity = to.noise;
        if (to.max_colors !== undefined) opts.maxColors = to.max_colors;
        if (to.min_area !== undefined) opts.minArea = to.min_area;
        if (to.ignore_white === true) opts.ignoreWhite = true;
        if (to.ignore_white === false) opts.ignoreWhite = false;
    }

    // Redraw to apply tracing
    app.redraw();

    // Expand the tracing to paths
    traceObj.tracing.expandTracing();

    // ── Export formats ───────────────────────────────────────────────────

    var formats = config.formats || ["svg"];

    for (var f = 0; f < formats.length; f++) {
        var fmt = formats[f].toLowerCase();

        if (fmt === "svg") {
            var svgOpts = new ExportOptionsSVG();
            svgOpts.embedRasterImages = false;
            svgOpts.fontType = SVGFontType.OUTLINEFONT;
            svgOpts.coordinatePrecision = 3;
            svgOpts.documentEncoding = SVGDocumentEncoding.UTF8;
            var svgFile = new File(outputDir + "/" + baseName + ".svg");
            doc.exportFile(svgFile, ExportType.SVG, svgOpts);
            exports.push(svgFile.fsName);
        }

        if (fmt === "ai") {
            var aiFile = new File(outputDir + "/" + baseName + ".ai");
            doc.saveAs(aiFile);
            exports.push(aiFile.fsName);
        }

        if (fmt === "eps") {
            var epsOpts = new EPSSaveOptions();
            epsOpts.compatibility = Compatibility.ILLUSTRATOR16;
            epsOpts.preview = EPSPreview.TRANSPARENTCOLORTIFF;
            var epsFile = new File(outputDir + "/" + baseName + ".eps");
            doc.saveAs(epsFile, epsOpts);
            exports.push(epsFile.fsName);
        }

        if (fmt === "pdf") {
            var pdfOpts = new PDFSaveOptions();
            pdfOpts.compatibility = PDFCompatibility.ACROBAT7;
            pdfOpts.preserveEditability = true;
            var pdfFile = new File(outputDir + "/" + baseName + ".pdf");
            doc.saveAs(pdfFile, pdfOpts);
            exports.push(pdfFile.fsName);
        }

        if (fmt === "png") {
            var pngOpts = new ExportOptionsPNG24();
            pngOpts.transparency = true;
            pngOpts.artBoardClipping = true;
            pngOpts.horizontalScale = config.png_scale || 100;
            pngOpts.verticalScale = config.png_scale || 100;
            var pngFile = new File(outputDir + "/" + baseName + "_vector.png");
            doc.exportFile(pngFile, ExportType.PNG24, pngOpts);
            exports.push(pngFile.fsName);
        }
    }

    // Close without saving (we already exported)
    doc.close(SaveOptions.DONOTSAVECHANGES);

    return exports;
}

// ── Main ─────────────────────────────────────────────────────────────────────

function main() {
    var result = {
        status: "error",
        images_processed: 0,
        exports: [],
        presets_available: [],
        errors: []
    };

    try {
        app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

        var config = readJSON(CONFIG_PATH);

        // List available presets for reference
        var presets = app.tracingPresetsList;
        for (var p = 0; p < presets.length; p++) {
            result.presets_available.push(presets[p]);
        }

        var outputDir = config.output_dir || Folder.desktop.fsName;
        // Ensure output folder exists
        var outFolder = new Folder(outputDir);
        if (!outFolder.exists) outFolder.create();

        var images = config.images || [];
        if (images.length === 0 && config.image) {
            images = [config.image];
        }

        for (var i = 0; i < images.length; i++) {
            var imgPath = images[i];
            var imgFile = new File(imgPath);
            var baseName = imgFile.name.substring(0, imgFile.name.lastIndexOf(".")) || imgFile.name;

            if (config.output_name && images.length === 1) {
                baseName = config.output_name;
            }

            try {
                var exports = vectorizeImage(imgPath, outputDir, baseName, config);
                for (var e = 0; e < exports.length; e++) {
                    result.exports.push(exports[e]);
                }
                result.images_processed++;
            } catch (imgErr) {
                result.errors.push(imgFile.name + ": " + imgErr.message);
            }
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

    return jsonStringify(result);
}

main();
