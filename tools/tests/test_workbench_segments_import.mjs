import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

const workbenchPath = new URL("../../assets/tools/ocr-translation-workbench.html", import.meta.url);
const fixturePath = new URL("../../automation-tests/dream-2013-12-p006-p007/output-v2/translation-segments.yml", import.meta.url);
const multiBoxFixturePath = new URL("../../automation-tests/wordpress-full-flow-20260825/translation-segments-llm.yml", import.meta.url);
const html = fs.readFileSync(workbenchPath, "utf8");
const yaml = fs.readFileSync(fixturePath, "utf8");
const multiBoxYaml = fs.readFileSync(multiBoxFixturePath, "utf8");
const start = html.indexOf("    function parseScalar(");
const end = html.indexOf("    function parseRegionsMarkdown(", start);

assert.notEqual(start, -1, "workbench YAML parser start was not found");
assert.notEqual(end, -1, "workbench YAML parser end was not found");

const context = { uid: () => "test-id" };
vm.createContext(context);
vm.runInContext(html.slice(start, end), context);

const segments = context.parseSegmentsYaml(yaml);
assert.equal(segments.length, 8, "all annotated regions should be imported");
assert.equal(segments[0].speaker, "采访上栏 1", "the first segment must not be skipped");
assert.equal(segments.filter((item) => item.kind === "image").length, 1);
assert.equal(segments.filter((item) => item.kind === "caption").length, 1);
assert.equal(segments.filter((item) => item.scanBox).length, 8);
assert.equal(segments.filter((item) => item.writingDirection === "horizontal").length, 6);
assert.equal(segments.filter((item) => item.writingDirection === "vertical").length, 1);
assert.equal(segments.at(-1).captionFor, "qwen-r14-v2");
assert.equal(segments[0].sourceImage, "E:\\Pokeamice\\scan\\DREAM 2013.12\\page007.jpg");

const multiBoxSegments = context.parseSegmentsYaml(multiBoxYaml);
const mergedBody = multiBoxSegments.find((item) => item.regionId === "qwen-r4");
assert.ok(mergedBody, "the merged interview body should be imported");
assert.equal(mergedBody.groupId, "continuous-qwen-r4-qwen-r5");
assert.equal(mergedBody.scanBoxes.length, 2, "all boxes in a merged reading segment must be retained");
assert.equal(mergedBody.scanBox, "246, 1265, 1649, 4267", "the first box remains editable in the workbench");

console.log("Workbench YAML import: regions retain image, caption, direction, source image, and multi-box groups.");
