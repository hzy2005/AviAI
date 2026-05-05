const { spawnSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const projectRoot = path.resolve(__dirname, "..");
const extraArgs = process.argv.slice(2);
const coverageRequested = extraArgs.includes("--coverage");
const testFiles = [
  "src/__tests__/page-interactions.test.js",
  "src/__tests__/api-mock.test.js",
  "src/__tests__/coverage-boost.test.js"
];

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    cwd: projectRoot,
    stdio: "inherit",
    ...options
  });

  if (typeof result.status === "number") {
    process.exitCode = result.status;
    return result.status;
  }

  throw result.error || new Error(`Failed to run ${command}`);
}

if (!coverageRequested) {
  run("node", ["--test", "--experimental-test-isolation=none", ...testFiles]);
  process.exit(process.exitCode || 0);
}

const coverageDir = path.join(projectRoot, "coverage");
const v8Dir = path.join(coverageDir, `v8-${Date.now()}`);

fs.mkdirSync(v8Dir, { recursive: true });

const testRun = spawnSync(
  "node",
  ["--test", "--experimental-test-isolation=none", "--experimental-test-coverage", ...testFiles],
  {
    cwd: projectRoot,
    stdio: "inherit",
    env: {
      ...process.env,
      NODE_V8_COVERAGE: v8Dir
    }
  }
);

if (typeof testRun.status === "number" && testRun.status !== 0) {
  process.exit(testRun.status);
}

run("node", ["scripts/write-lcov.js", v8Dir]);
