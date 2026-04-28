const fs = require("fs");
const path = require("path");
const { fileURLToPath } = require("url");

const projectRoot = path.resolve(__dirname, "..");
const coverageDir = path.join(projectRoot, "coverage");
const v8Dir = path.resolve(process.argv[2] || path.join(coverageDir, "v8"));
const lcovPath = path.join(coverageDir, "lcov.info");
const summaryPath = path.join(coverageDir, "coverage-summary.json");

const SOURCE_ROOTS = [
  path.join(projectRoot, "config"),
  path.join(projectRoot, "pages"),
  path.join(projectRoot, "src", "api"),
  path.join(projectRoot, "utils")
];

function normalizePath(filePath) {
  return path.normalize(filePath);
}

function shouldInclude(filePath) {
  const normalized = normalizePath(filePath);
  if (!normalized.endsWith(".js")) {
    return false;
  }

  if (normalized.includes(`${path.sep}__tests__${path.sep}`)) {
    return false;
  }

  return SOURCE_ROOTS.some((root) => normalized.startsWith(normalizePath(root) + path.sep));
}

function getCoverageEntries() {
  if (!fs.existsSync(v8Dir)) {
    throw new Error("coverage/v8 not found. Run tests with coverage first.");
  }

  const jsonFiles = fs.readdirSync(v8Dir)
    .filter((name) => name.endsWith(".json"))
    .map((name) => path.join(v8Dir, name));

  const byFile = new Map();

  jsonFiles.forEach((file) => {
    const payload = JSON.parse(fs.readFileSync(file, "utf8"));
    (payload.result || []).forEach((entry) => {
      if (!entry.url || !entry.url.startsWith("file:")) {
        return;
      }

      let filePath = "";
      try {
        filePath = fileURLToPath(entry.url);
      } catch (error) {
        return;
      }

      if (!shouldInclude(filePath)) {
        return;
      }

      const normalized = normalizePath(filePath);
      if (!byFile.has(normalized)) {
        byFile.set(normalized, []);
      }
      byFile.get(normalized).push(...(entry.functions || []).flatMap((fn) => fn.ranges || []));
    });
  });

  return byFile;
}

function getLineStarts(source) {
  const starts = [0];
  for (let index = 0; index < source.length; index += 1) {
    if (source[index] === "\n") {
      starts.push(index + 1);
    }
  }
  return starts;
}

function findLineNumber(lineStarts, offset) {
  let low = 0;
  let high = lineStarts.length - 1;

  while (low <= high) {
    const mid = Math.floor((low + high) / 2);
    if (lineStarts[mid] <= offset) {
      low = mid + 1;
    } else {
      high = mid - 1;
    }
  }

  return Math.max(0, high) + 1;
}

function getLineCoverage(filePath, ranges) {
  const source = fs.readFileSync(filePath, "utf8");
  const lineStarts = getLineStarts(source);
  const points = new Set([0, source.length]);

  lineStarts.forEach((start, index) => {
    points.add(start);
    const nextStart = index + 1 < lineStarts.length ? lineStarts[index + 1] : source.length;
    points.add(nextStart);
  });

  ranges.forEach((range) => {
    points.add(range.startOffset);
    points.add(range.endOffset);
  });

  const sortedPoints = [...points]
    .filter((point) => point >= 0 && point <= source.length)
    .sort((a, b) => a - b);

  const executable = new Set();
  const covered = new Set();

  for (let index = 0; index < sortedPoints.length - 1; index += 1) {
    const start = sortedPoints[index];
    const end = sortedPoints[index + 1];
    if (end <= start) {
      continue;
    }

    const midpoint = start;
    const matching = ranges.filter(
      (range) => range.startOffset <= midpoint && midpoint < range.endOffset
    );

    if (!matching.length) {
      continue;
    }

    matching.sort((left, right) => {
      const leftSize = left.endOffset - left.startOffset;
      const rightSize = right.endOffset - right.startOffset;
      return leftSize - rightSize;
    });

    const activeRange = matching[0];
    const startLine = findLineNumber(lineStarts, start);
    const endLine = findLineNumber(lineStarts, Math.max(start, end - 1));

    for (let line = startLine; line <= endLine; line += 1) {
      executable.add(line);
      if (activeRange.count > 0) {
        covered.add(line);
      }
    }
  }

  return {
    executable: [...executable].sort((a, b) => a - b),
    covered
  };
}

function writeReports(entries) {
  let totalFound = 0;
  let totalHit = 0;
  const lines = [];
  const summary = {
    generatedAt: new Date().toISOString(),
    files: {}
  };

  [...entries.keys()].sort().forEach((filePath) => {
    const { executable, covered } = getLineCoverage(filePath, entries.get(filePath));
    const relativePath = path.relative(projectRoot, filePath).replace(/\\/g, "/");

    lines.push(`SF:${relativePath}`);
    executable.forEach((lineNumber) => {
      const hit = covered.has(lineNumber) ? 1 : 0;
      lines.push(`DA:${lineNumber},${hit}`);
    });
    lines.push(`LF:${executable.length}`);
    lines.push(`LH:${executable.filter((lineNumber) => covered.has(lineNumber)).length}`);
    lines.push("end_of_record");

    totalFound += executable.length;
    totalHit += executable.filter((lineNumber) => covered.has(lineNumber)).length;
    summary.files[relativePath] = {
      lines: {
        found: executable.length,
        hit: executable.filter((lineNumber) => covered.has(lineNumber)).length,
        pct: executable.length ? Number(((covered.size / executable.length) * 100).toFixed(2)) : 100
      }
    };
  });

  summary.total = {
    lines: {
      found: totalFound,
      hit: totalHit,
      pct: totalFound ? Number(((totalHit / totalFound) * 100).toFixed(2)) : 100
    }
  };

  fs.writeFileSync(lcovPath, `${lines.join("\n")}\n`, "utf8");
  fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2), "utf8");
}

writeReports(getCoverageEntries());
