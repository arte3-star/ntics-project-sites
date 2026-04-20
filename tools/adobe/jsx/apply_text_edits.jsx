/**
 * apply_text_edits.jsx — Aplica edicoes de texto no documento ativo do Illustrator.
 *
 * Executado via COM (app.DoJavaScript) pelo wrapper Python.
 * Le config JSON com lista de edicoes (replace, delete, insert).
 * Grava resultado em _result.json ao finalizar.
 *
 * Variavel CONFIG_PATH e injetada pelo Python antes da execucao.
 *
 * Config JSON schema:
 *   {
 *     "edits": [
 *       {"type": "replace", "original_text": "old", "new_text": "new", "page": 1},
 *       {"type": "delete", "original_text": "to remove", "page": 2},
 *       {"type": "insert", "after_text": "context", "new_text": "to insert", "page": 1}
 *     ],
 *     "match_mode": "exact|contains|fuzzy",
 *     "case_sensitive": true,
 *     "dry_run": false,
 *     "output_dir": "C:/path/to/output"
 *   }
 */

// CONFIG_PATH is injected by Python wrapper before execution
// var CONFIG_PATH = "C:/path/to/edits_config.json";

// -- Helpers ------------------------------------------------------------------

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

// -- Text normalization -------------------------------------------------------

function normalizeWhitespace(str) {
    // Collapse multiple whitespace (including line breaks) into single space
    return str.replace(/[\s\r\n]+/g, " ").replace(/^\s+|\s+$/g, "");
}

function textContains(haystack, needle, caseSensitive) {
    if (!caseSensitive) {
        return normalizeWhitespace(haystack).toLowerCase().indexOf(normalizeWhitespace(needle).toLowerCase()) >= 0;
    }
    return normalizeWhitespace(haystack).indexOf(normalizeWhitespace(needle)) >= 0;
}

function textEquals(a, b, caseSensitive) {
    var na = normalizeWhitespace(a);
    var nb = normalizeWhitespace(b);
    if (!caseSensitive) {
        return na.toLowerCase() === nb.toLowerCase();
    }
    return na === nb;
}

/**
 * Fuzzy match: returns true if needle is "close enough" to haystack.
 * Allows small differences (punctuation, extra spaces, minor typos).
 */
function fuzzyMatch(haystack, needle, caseSensitive) {
    var h = normalizeWhitespace(haystack);
    var n = normalizeWhitespace(needle);
    if (!caseSensitive) {
        h = h.toLowerCase();
        n = n.toLowerCase();
    }
    // Exact match
    if (h === n) return true;
    // Contains match
    if (h.indexOf(n) >= 0) return true;
    // Strip punctuation and compare
    var hClean = h.replace(/[.,;:!?'"()\-\u2013\u2014]/g, "").replace(/\s+/g, " ");
    var nClean = n.replace(/[.,;:!?'"()\-\u2013\u2014]/g, "").replace(/\s+/g, " ");
    if (hClean === nClean) return true;
    if (hClean.indexOf(nClean) >= 0) return true;
    return false;
}

// -- Artboard/page mapping ----------------------------------------------------

/**
 * Map a page number to an artboard index.
 * In Illustrator, each artboard typically corresponds to a page.
 * If the document has fewer artboards than pages, we search all.
 */
function getArtboardTextFrames(doc, pageNum) {
    // If no page specified or only 1 artboard, return all text frames
    if (!pageNum || doc.artboards.length <= 1) {
        return doc.textFrames;
    }

    var abIndex = pageNum - 1;
    if (abIndex < 0 || abIndex >= doc.artboards.length) {
        return doc.textFrames; // Fallback: search all
    }

    // Get artboard rect
    var abRect = doc.artboards[abIndex].artboardRect;
    // [left, top, right, bottom] — note: top > bottom in Illustrator coords

    // Filter text frames that overlap with this artboard
    var frames = [];
    for (var i = 0; i < doc.textFrames.length; i++) {
        var tf = doc.textFrames[i];
        var tfLeft = tf.left;
        var tfTop = tf.top;
        var tfRight = tfLeft + tf.width;
        var tfBottom = tfTop - tf.height;

        // Check overlap with artboard
        if (tfRight > abRect[0] && tfLeft < abRect[2] &&
            tfTop > abRect[3] && tfBottom < abRect[1]) {
            frames.push(tf);
        }
    }

    return frames;
}

// -- Edit operations ----------------------------------------------------------

/**
 * Replace text in a text frame.
 * Handles both full-content replacement and substring replacement.
 * Preserves formatting when doing substring replacement.
 */
function replaceInTextFrame(tf, originalText, newText, matchMode, caseSensitive) {
    var content = tf.contents;
    var normalizedContent = normalizeWhitespace(content);
    var normalizedOriginal = normalizeWhitespace(originalText);

    // Check match based on mode
    var isMatch = false;
    if (matchMode === "exact") {
        isMatch = textEquals(content, originalText, caseSensitive);
    } else if (matchMode === "fuzzy") {
        isMatch = fuzzyMatch(content, originalText, caseSensitive);
    } else {
        // "contains" mode (default)
        isMatch = textContains(content, originalText, caseSensitive);
    }

    if (!isMatch) return false;

    // Full content replacement (exact match or content is just the target text)
    if (textEquals(content, originalText, caseSensitive)) {
        tf.contents = newText;
        return true;
    }

    // Substring replacement — find and replace within content
    // We need to handle the case where the text might span lines differently
    var searchStr = caseSensitive ? normalizedOriginal : normalizedOriginal.toLowerCase();
    var targetStr = caseSensitive ? normalizedContent : normalizedContent.toLowerCase();
    var idx = targetStr.indexOf(searchStr);

    if (idx >= 0) {
        // Map back to original content positions (accounting for whitespace normalization)
        // Simple approach: try direct replacement first
        if (content.indexOf(originalText) >= 0) {
            tf.contents = content.replace(originalText, newText);
            return true;
        }

        // If normalized match, replace in normalized form and set
        var before = normalizedContent.substring(0, idx);
        var after = normalizedContent.substring(idx + normalizedOriginal.length);
        tf.contents = before + newText + after;
        return true;
    }

    return false;
}

/**
 * Delete text from a text frame.
 * If the entire content matches, removes the text frame.
 * If partial match, removes just that portion.
 */
function deleteFromTextFrame(tf, originalText, matchMode, caseSensitive) {
    var content = tf.contents;

    if (textEquals(content, originalText, caseSensitive)) {
        // Full match — mark for removal (caller handles)
        tf.contents = "";
        return "full";
    }

    if (textContains(content, originalText, caseSensitive)) {
        // Partial match — remove substring
        if (content.indexOf(originalText) >= 0) {
            tf.contents = content.replace(originalText, "");
        } else {
            var norm = normalizeWhitespace(content);
            var normOrig = normalizeWhitespace(originalText);
            var idx = caseSensitive ? norm.indexOf(normOrig) : norm.toLowerCase().indexOf(normOrig.toLowerCase());
            if (idx >= 0) {
                tf.contents = norm.substring(0, idx) + norm.substring(idx + normOrig.length);
            }
        }
        return "partial";
    }

    return false;
}

// -- Main ---------------------------------------------------------------------

function main() {
    var result = {
        status: "error",
        total_edits: 0,
        applied: 0,
        skipped: 0,
        not_found: 0,
        details: [],
        errors: []
    };

    try {
        app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

        var config = readJSON(CONFIG_PATH);
        var doc = app.activeDocument;
        var edits = config.edits || [];
        var matchMode = config.match_mode || "contains";
        var caseSensitive = config.case_sensitive !== false; // default true
        var dryRun = config.dry_run === true;

        result.total_edits = edits.length;
        result.dry_run = dryRun;

        // Process each edit
        for (var e = 0; e < edits.length; e++) {
            var edit = edits[e];
            var editResult = {
                index: e,
                type: edit.type,
                original_text: edit.original_text || "",
                new_text: edit.new_text || "",
                status: "not_found",
                frame_name: ""
            };

            // Get relevant text frames (filtered by page/artboard if specified)
            var frames;
            if (edit.page) {
                frames = getArtboardTextFrames(doc, edit.page);
            } else {
                frames = doc.textFrames;
            }

            // Convert frames collection to array for consistent iteration
            var frameArray = [];
            if (frames.length !== undefined) {
                for (var fi = 0; fi < frames.length; fi++) {
                    frameArray.push(frames[fi]);
                }
            }

            var found = false;

            for (var f = 0; f < frameArray.length; f++) {
                var tf = frameArray[f];

                if (edit.type === "replace") {
                    if (!edit.original_text || !edit.new_text) {
                        editResult.status = "skipped";
                        editResult.reason = "missing original_text or new_text";
                        break;
                    }

                    // Check if this frame contains the target text
                    var hasMatch = false;
                    if (matchMode === "exact") {
                        hasMatch = textEquals(tf.contents, edit.original_text, caseSensitive);
                    } else if (matchMode === "fuzzy") {
                        hasMatch = fuzzyMatch(tf.contents, edit.original_text, caseSensitive);
                    } else {
                        hasMatch = textContains(tf.contents, edit.original_text, caseSensitive);
                    }

                    if (hasMatch) {
                        editResult.frame_name = tf.name || ("TextFrame " + f);
                        editResult.frame_contents_before = tf.contents.substring(0, 100);

                        if (!dryRun) {
                            var replaced = replaceInTextFrame(tf, edit.original_text, edit.new_text, matchMode, caseSensitive);
                            if (replaced) {
                                editResult.status = "applied";
                                editResult.frame_contents_after = tf.contents.substring(0, 100);
                                found = true;
                                break;
                            }
                        } else {
                            editResult.status = "would_apply";
                            found = true;
                            break;
                        }
                    }

                } else if (edit.type === "delete") {
                    if (!edit.original_text) {
                        editResult.status = "skipped";
                        editResult.reason = "missing original_text";
                        break;
                    }

                    var hasDeleteMatch = textContains(tf.contents, edit.original_text, caseSensitive) ||
                                         textEquals(tf.contents, edit.original_text, caseSensitive);

                    if (hasDeleteMatch) {
                        editResult.frame_name = tf.name || ("TextFrame " + f);
                        editResult.frame_contents_before = tf.contents.substring(0, 100);

                        if (!dryRun) {
                            var deleteResult = deleteFromTextFrame(tf, edit.original_text, matchMode, caseSensitive);
                            if (deleteResult) {
                                editResult.status = "applied";
                                editResult.delete_scope = deleteResult;
                                found = true;
                                break;
                            }
                        } else {
                            editResult.status = "would_apply";
                            found = true;
                            break;
                        }
                    }

                } else if (edit.type === "insert") {
                    // Insert after a context string
                    var afterText = edit.after_text || edit.original_text || "";
                    if (!afterText && !edit.new_text) {
                        editResult.status = "skipped";
                        editResult.reason = "missing context and new_text";
                        break;
                    }

                    if (afterText && textContains(tf.contents, afterText, caseSensitive)) {
                        editResult.frame_name = tf.name || ("TextFrame " + f);
                        editResult.frame_contents_before = tf.contents.substring(0, 100);

                        if (!dryRun) {
                            var insertIdx = tf.contents.indexOf(afterText);
                            if (insertIdx >= 0) {
                                var insertPos = insertIdx + afterText.length;
                                tf.contents = tf.contents.substring(0, insertPos) + edit.new_text + tf.contents.substring(insertPos);
                                editResult.status = "applied";
                                editResult.frame_contents_after = tf.contents.substring(0, 100);
                                found = true;
                                break;
                            }
                        } else {
                            editResult.status = "would_apply";
                            found = true;
                            break;
                        }
                    }
                }
            }

            if (!found && editResult.status === "not_found") {
                result.not_found++;
            } else if (editResult.status === "skipped") {
                result.skipped++;
            } else if (editResult.status === "applied" || editResult.status === "would_apply") {
                result.applied++;
            }

            result.details.push(editResult);
        }

        result.status = result.not_found > 0 ? "partial" : "success";

    } catch (err) {
        result.status = "error";
        result.errors.push(err.message);
    } finally {
        try { app.userInteractionLevel = UserInteractionLevel.DISPLAYALERTS; } catch (e) {}
    }

    // Write result JSON
    var resultPath = CONFIG_PATH.replace(".json", "_result.json");
    writeJSON(resultPath, result);

    return jsonStringify(result);
}

main();
